import os
import sys
import sqlite3
import numpy as np
from numpy.linalg import norm
import ollama
import logging
import json
import csv
import tiktoken
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Optional
from .utils import render_markdown_to_html
import re

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_TOKENS = 8191
DEFAULT_DB_PATH = ".clai.db"
DEFAULT_MODEL_NAME = "nomic-embed-text:latest"
DEFAULT_PROVIDER = "ollama"
DEFAULT_CHAT_MODEL = os.environ.get("CHAT_MODEL", "llama3.2:1b")
MAX_CHUNK_SIZE = 32000
OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")

FILE_LOADERS = {
    ".txt": lambda p: open(p, "r", encoding="utf-8").read(),
    ".md": lambda p: open(p, "r", encoding="utf-8").read(),
    ".py": lambda p: open(p, "r", encoding="utf-8").read(),
    ".json": lambda p: json.dumps(json.load(open(p, "r", encoding="utf-8")), indent=2),
    ".csv": lambda p: "\n".join([", ".join(row) for row in csv.reader(open(p, "r", encoding="utf-8"))])
}

SYSTEM_PROMPT = (
    "You are an assistant that identifies the most feature-complete and robust version of code files "
    "based on the provided context."
)

def init_db(db_path: str) -> sqlite3.Connection:
    """
    Initialize SQLite database with tables for documents and embeddings.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS documents")
    c.execute("DROP TABLE IF EXISTS embeddings")
    c.execute("DROP TABLE IF EXISTS files")
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            chunk_idx INTEGER,
            content TEXT,
            UNIQUE(filename, chunk_idx)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            doc_id INTEGER PRIMARY KEY,
            embedding BLOB,
            FOREIGN KEY(doc_id) REFERENCES documents(id)
        )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS files (
        filename TEXT PRIMARY KEY,
        mtime REAL
    )
    """)
    conn.commit()
    return conn

def get_embedding(text: str, model: str, provider: str = DEFAULT_PROVIDER) -> np.ndarray:
    """Get embedding from Ollama API using specified model"""
    resp = ollama.embed(model=model, input=text)
    emb = resp["embeddings"]
    return np.array(emb, dtype=np.float32)

def _insert_chunk(cursor, filename, idx, text):
    cursor.execute(
        "INSERT OR IGNORE INTO documents (filename, chunk_idx, content) VALUES (?, ?, ?)",
        (filename, idx, text)
    )
    cursor.connection.commit()

def run_python_code_func(code: str) -> str:
    """Execute Python code in a temp file and return stdout or stderr."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        proc = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            check=False
        )
        os.unlink(temp_path)
        if proc.stderr:
            return f"Error:\n{proc.stderr}"
        return proc.stdout or ""
    except Exception as e:
        return f"Error running Python code: {e}"

def run_bash_command_func(command: str) -> str:
    """Execute a bash command safely and return stdout or stderr."""
    unsafe = ['sudo', 'rm -rf', '>', '>>', '|', '&', ';']
    if any(tok in command for tok in unsafe):
        return "Error: Command contains unsafe operations"
    try:
        proc = subprocess.run(
            ['sh', '-c', command],
            capture_output=True,
            text=True,
            check=False
        )
        if proc.stderr:
            return f"Error:\n{proc.stderr}"
        return proc.stdout or ""
    except Exception as e:
        return f"Error running bash command: {e}"

def ingest_files(directory: str, db_path: str, model_name: str, provider: str, recursive: bool, exclude_patterns: Optional[List[str]] = None) -> None:
    """
    Ingest files with plugin loaders, chunk by token boundaries,
    skip unchanged files, and enqueue embedding tasks.
    """
    import fnmatch
    
    if exclude_patterns is None:
        exclude_patterns = []
    
    walker = os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]
    conn = init_db(db_path)
    c = conn.cursor()
    encoder = tiktoken.get_encoding("cl100k_base")
    logger.info(f"Using 'cl100k_base' tokenizer for model {model_name}")
    embed_tasks = []
    for root, dirs, files in walker:
        for fname in files:
            path = os.path.join(root, fname)
            rel_path = os.path.relpath(path, directory) if recursive else fname
            
            # Check exclude patterns
            if any(fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(fname, pattern) 
                   for pattern in exclude_patterns):
                logger.debug(f"Excluding file: {rel_path}")
                continue
            
            ext = os.path.splitext(fname)[1].lower()
            loader = FILE_LOADERS.get(ext)
            if not loader or not os.path.isfile(path):
                logger.debug(f"Skipping unsupported or non-file: {rel_path}")
                continue
            mtime = os.path.getmtime(path)
            c.execute("SELECT mtime FROM files WHERE filename = ?", (rel_path,))
            row = c.fetchone()
            if row and row[0] == mtime:
                logger.info(f"Skipping unchanged file: {rel_path}")
                continue
            try:
                content = loader(path).strip()
            except Exception as e:
                logger.warning(f"Error loading {rel_path}: {e}")
                continue
            if not content:
                continue
            paragraphs = re.split(r'\n\s*\n', content)
            token_buffer = []
            for para in paragraphs:
                para_tokens = encoder.encode(para, disallowed_special=())
                if len(token_buffer) + len(para_tokens) > MAX_TOKENS:
                    text_chunk = encoder.decode(token_buffer)
                    _insert_chunk(c, rel_path, len(embed_tasks), text_chunk)
                    embed_tasks.append((rel_path, text_chunk))
                    token_buffer = para_tokens
                else:
                    token_buffer += para_tokens
            if token_buffer:
                text_chunk = encoder.decode(token_buffer)
                _insert_chunk(c, rel_path, len(embed_tasks), text_chunk)
                embed_tasks.append((rel_path, text_chunk))
            c.execute("INSERT OR REPLACE INTO files (filename, mtime) VALUES (?, ?)", (rel_path, mtime))
            conn.commit()
    conn.close()
    logger.info(f"Queued {len(embed_tasks)} chunks for embedding")
    def embed_worker(task):
        rel_path, chunk = task
        conn_thread = sqlite3.connect(db_path, check_same_thread=False)
        c_thread = conn_thread.cursor()
        c_thread.execute("SELECT id FROM documents WHERE filename = ? AND content = ?", (rel_path, chunk))
        row = c_thread.fetchone()
        if not row:
            return
        doc_id = row[0]
        try:
            emb = get_embedding(chunk, model_name, provider)
            emb_blob = emb.tobytes()
            c_thread.execute("INSERT OR REPLACE INTO embeddings (doc_id, embedding) VALUES (?, ?)", (doc_id, emb_blob))
            conn_thread.commit()
            logger.info(f"Embedded {rel_path} (doc_id={doc_id})")
        except Exception as e:
            logger.error(f"Error embedding {rel_path}: {e}")
        finally:
            conn_thread.close()
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(embed_worker, embed_tasks))

def search_embeddings(query: str, db_path: str, model_name: str, top_k: int, provider: str = DEFAULT_PROVIDER) -> list:
    """
    Search the SQLite DB for the top_k documents most similar to the query.
    """
    query_emb = get_embedding(query, model_name, provider)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT doc_id, embedding FROM embeddings")
    scores = []
    for doc_id, emb_blob in c.fetchall():
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        sim = np.dot(query_emb, emb) / (norm(query_emb) * norm(emb))
        sim = sim.item() if hasattr(sim, "item") else float(sim)
        scores.append((doc_id, sim))
    conn.close()
    scores.sort(key=lambda x: x[1], reverse=True)
    top = scores[:top_k]
    results = []
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for doc_id, score in top:
        c.execute("SELECT filename, content FROM documents WHERE id = ?", (doc_id,))
        fname, content = c.fetchone()
        results.append((fname, content, score))
    conn.close()
    return results

def chat(
    db: str = DEFAULT_DB_PATH,
    model: str = DEFAULT_MODEL_NAME,
    provider: str = DEFAULT_PROVIDER,
    chat_model: str = DEFAULT_CHAT_MODEL,
    topk: int = 3,
    user_input: Optional[str] = None,
    history: Optional[list] = None
) -> str:
    """
    Run a chat session or single chat turn. Returns the assistant's response as Markdown.
    """
    if history is None:
        history = []
    
    if user_input is None:
        raise ValueError("user_input is required")
    
    # Search for relevant documents
    docs = search_embeddings(user_input, db, model, topk, provider)
    context = ""
    for fname, content, score in docs:
        context += f"== {fname} (score={score:.4f}) ==\n{content}\n\n"
    
    # Build the prompt with context
    prompt_text = f"""Based on the following context from documents, please answer the question.

Context:
{context}

Question: {user_input}

Please provide a helpful answer based on the context provided. If the context doesn't contain relevant information, say so clearly."""
    
    # Prepare messages for chat
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history.copy() + [{"role": "user", "content": prompt_text}]
    
    # Define available tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_python_code",
                "description": "Execute Python code and return the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code to run"}
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "run_bash_command",
                "description": "Execute a bash command and return the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Bash command to run"}
                    },
                    "required": ["command"]
                }
            }
        }
    ]
    
    try:
        # Try with tools first
        response = ollama.chat(
            model=chat_model,
            messages=messages,
            tools=tools,
            stream=False
        )
    except Exception as e:
        if "does not support tools" in str(e):
            # Fallback to chat without tools
            logger.info(f"Model {chat_model} doesn't support tools, falling back to simple chat")
            response = ollama.chat(
                model=chat_model,
                messages=messages,
                stream=False
            )
        else:
            raise e
    
    try:
        
        # Handle response based on ollama API structure  
        if isinstance(response, dict):
            msg = response.get("message", {})
        else:
            msg = response.message if hasattr(response, "message") else {}
        
        # Check for tool calls
        if isinstance(msg, dict) and msg.get("tool_calls"):
            tool_calls = msg["tool_calls"]
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
                
                if function_name == "run_python_code":
                    tool_result = run_python_code_func(arguments["code"])
                elif function_name == "run_bash_command":
                    tool_result = run_bash_command_func(arguments["command"])
                else:
                    tool_result = f"Unknown function: {function_name}"
                
                # Add tool result to messages and get final response
                tool_message = {
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result
                }
                
                followup = ollama.chat(
                    model=chat_model,
                    messages=messages + [msg, tool_message],
                    stream=False
                )
                
                if isinstance(followup, dict):
                    followup_msg = followup.get("message", {})
                else:
                    followup_msg = followup.message if hasattr(followup, "message") else {}
                
                answer = followup_msg.get("content", "") if isinstance(followup_msg, dict) else getattr(followup_msg, "content", "")
                break
        else:
            # No tool calls, just return the content
            answer = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
        
        return render_markdown_to_html(answer) if answer else "I'm sorry, I couldn't generate a response."
        
    except Exception as e:
        logger.error(f"Error in chat function: {e}")
        return f"Error generating response: {e}" 