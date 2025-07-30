"""
Llamaball - Core RAG Functionality
File Purpose: Core RAG system with comprehensive file parsing and performance optimization
Primary Functions: Document ingestion, embedding generation, semantic search, chat
Inputs: Files, queries, chat messages
Outputs: Embeddings, search results, chat responses
"""

import logging
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Tuple, Dict, Union
from pathlib import Path

import numpy as np
import ollama
import requests
import tiktoken
from numpy.linalg import norm

from .utils import render_markdown_to_html
from .parsers import FileParser, is_supported_file, get_supported_extensions

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_TOKENS = 8191
DEFAULT_DB_PATH = ".llamaball.db"
DEFAULT_MODEL_NAME = "nomic-embed-text:latest"
DEFAULT_PROVIDER = "ollama"
DEFAULT_CHAT_MODEL = os.environ.get("CHAT_MODEL", "llama3.2:1b")
MAX_CHUNK_SIZE = 32000
OLLAMA_ENDPOINT = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")

# Initialize file parser
file_parser = FileParser()

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
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            chunk_idx INTEGER,
            content TEXT,
            UNIQUE(filename, chunk_idx)
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS embeddings (
            doc_id INTEGER PRIMARY KEY,
            embedding BLOB,
            FOREIGN KEY(doc_id) REFERENCES documents(id)
        )
    """
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS files (
        filename TEXT PRIMARY KEY,
        mtime REAL
    )
    """
    )
    conn.commit()
    return conn


def get_embedding(
    text: str, model: str, provider: str = DEFAULT_PROVIDER
) -> np.ndarray:
    """Get embedding from Ollama API using specified model"""
    resp = ollama.embed(model=model, input=text)
    emb = resp["embeddings"]
    return np.array(emb, dtype=np.float32)


def _insert_chunk(cursor, filename, idx, text):
    cursor.execute(
        "INSERT OR IGNORE INTO documents (filename, chunk_idx, content) VALUES (?, ?, ?)",
        (filename, idx, text),
    )
    cursor.connection.commit()


def run_python_code_func(code: str) -> str:
    """Execute Python code in a temp file and return stdout or stderr."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        proc = subprocess.run(
            [sys.executable, temp_path], capture_output=True, text=True, check=False
        )
        os.unlink(temp_path)
        if proc.stderr:
            return f"Error:\n{proc.stderr}"
        return proc.stdout or ""
    except Exception as e:
        return f"Error running Python code: {e}"


def run_bash_command_func(command: str) -> str:
    """Execute a bash command safely and return stdout or stderr."""
    unsafe = ["sudo", "rm -rf", ">", ">>", "|", "&", ";"]
    if any(tok in command for tok in unsafe):
        return "Error: Command contains unsafe operations"
    try:
        proc = subprocess.run(
            ["sh", "-c", command], capture_output=True, text=True, check=False
        )
        if proc.stderr:
            return f"Error:\n{proc.stderr}"
        return proc.stdout or ""
    except Exception as e:
        return f"Error running bash command: {e}"


def ingest_files(
    directory: str,
    db_path: str,
    model_name: str,
    provider: str,
    recursive: bool,
    exclude_patterns: Optional[List[str]] = None,
    force: bool = False,
) -> Dict[str, Union[int, List[str]]]:
    """
    Ingest files with comprehensive parsing, chunk by token boundaries,
    skip unchanged files, and enqueue embedding tasks.
    
    Returns:
        Dictionary with statistics about ingestion process
        
    Performance:
        - Multi-threaded embedding generation
        - Intelligent file change detection
        - Memory-efficient chunking
        - Comprehensive error handling
    """
    import fnmatch

    if exclude_patterns is None:
        exclude_patterns = []

    walker = (
        os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]
    )
    conn = init_db(db_path)
    c = conn.cursor()
    encoder = tiktoken.get_encoding("cl100k_base")
    logger.info(f"Using 'cl100k_base' tokenizer for model {model_name}")
    
    # Statistics tracking
    stats = {
        'processed_files': 0,
        'skipped_files': 0,
        'error_files': 0,
        'total_chunks': 0,
        'supported_extensions': list(get_supported_extensions()),
        'processed_extensions': set(),
        'error_messages': []
    }
    
    embed_tasks = []
    
    for root, dirs, files in walker:
        for fname in files:
            path = os.path.join(root, fname)
            rel_path = os.path.relpath(path, directory) if recursive else fname

            # Check exclude patterns
            if any(
                fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(fname, pattern)
                for pattern in exclude_patterns
            ):
                logger.debug(f"Excluding file: {rel_path}")
                stats['skipped_files'] += 1
                continue

            # Check if file type is supported
            if not is_supported_file(path):
                logger.debug(f"Skipping unsupported file type: {rel_path}")
                stats['skipped_files'] += 1
                continue
                
            if not os.path.isfile(path):
                logger.debug(f"Skipping non-file: {rel_path}")
                stats['skipped_files'] += 1
                continue
                
            # Check if file has changed (unless force mode)
            if not force:
                mtime = os.path.getmtime(path)
                c.execute("SELECT mtime FROM files WHERE filename = ?", (rel_path,))
                row = c.fetchone()
                if row and row[0] == mtime:
                    logger.info(f"Skipping unchanged file: {rel_path}")
                    stats['skipped_files'] += 1
                    continue
            
            # Parse file content
            try:
                parse_result = file_parser.parse_file(path)
                
                if parse_result['error']:
                    error_msg = parse_result['error']
                    # Categorize errors for better user experience
                    if "not available" in error_msg and "Install with:" in error_msg:
                        logger.info(f"Optional dependency missing for {rel_path}: {error_msg}")
                        stats['skipped_files'] += 1
                        continue
                    elif "corrupted" in error_msg or "not a valid" in error_msg:
                        logger.warning(f"Corrupted file {rel_path}: {error_msg}")
                        stats['error_files'] += 1
                        stats['error_messages'].append(f"{rel_path}: {error_msg}")
                        continue
                    elif "password protected" in error_msg or "encrypted" in error_msg:
                        logger.warning(f"Protected file {rel_path}: {error_msg}")
                        stats['error_files'] += 1
                        stats['error_messages'].append(f"{rel_path}: {error_msg}")
                        continue
                    else:
                        logger.warning(f"Error parsing {rel_path}: {error_msg}")
                        stats['error_files'] += 1
                        stats['error_messages'].append(f"{rel_path}: {error_msg}")
                        continue
                
                content = parse_result['content'].strip()
                if not content:
                    logger.debug(f"Empty content for {rel_path}")
                    stats['skipped_files'] += 1
                    continue
                    
                # Track file extension
                ext = Path(path).suffix.lower()
                stats['processed_extensions'].add(ext)
                    
            except Exception as e:
                logger.warning(f"Unexpected error loading {rel_path}: {e}")
                stats['error_files'] += 1
                stats['error_messages'].append(f"{rel_path}: Unexpected error - {str(e)}")
                continue
            
            # Chunk content by token boundaries
            paragraphs = re.split(r"\n\s*\n", content)
            token_buffer = []
            chunk_count = 0
            
            for para in paragraphs:
                para_tokens = encoder.encode(para, disallowed_special=())
                if len(token_buffer) + len(para_tokens) > MAX_TOKENS:
                    if token_buffer:  # Only create chunk if buffer has content
                        text_chunk = encoder.decode(token_buffer)
                        _insert_chunk(c, rel_path, chunk_count, text_chunk)
                        embed_tasks.append((rel_path, text_chunk, chunk_count))
                        chunk_count += 1
                        stats['total_chunks'] += 1
                    token_buffer = para_tokens
                else:
                    token_buffer += para_tokens
            
            # Handle remaining buffer
            if token_buffer:
                text_chunk = encoder.decode(token_buffer)
                _insert_chunk(c, rel_path, chunk_count, text_chunk)
                embed_tasks.append((rel_path, text_chunk, chunk_count))
                stats['total_chunks'] += 1
            
            # Update file modification time
            mtime = os.path.getmtime(path)
            c.execute(
                "INSERT OR REPLACE INTO files (filename, mtime) VALUES (?, ?)",
                (rel_path, mtime),
            )
            conn.commit()
            
            stats['processed_files'] += 1
            logger.info(f"Processed {rel_path} -> {chunk_count + 1 if token_buffer else chunk_count} chunks")
    
    conn.close()
    
    # Convert processed_extensions set to list for JSON serialization
    stats['processed_extensions'] = list(stats['processed_extensions'])
    
    logger.info(f"Queued {len(embed_tasks)} chunks for embedding from {stats['processed_files']} files")
    logger.info(f"Processed file types: {', '.join(stats['processed_extensions'])}")
    
    if stats['error_files'] > 0:
        logger.warning(f"Encountered errors in {stats['error_files']} files")

    # Parallel embedding generation
    def embed_worker(task):
        rel_path, chunk, chunk_idx = task
        conn_thread = sqlite3.connect(db_path, check_same_thread=False)
        c_thread = conn_thread.cursor()
        c_thread.execute(
            "SELECT id FROM documents WHERE filename = ? AND content = ?",
            (rel_path, chunk),
        )
        row = c_thread.fetchone()
        if not row:
            conn_thread.close()
            return
        doc_id = row[0]
        try:
            emb = get_embedding(chunk, model_name, provider)
            emb_blob = emb.tobytes()
            c_thread.execute(
                "INSERT OR REPLACE INTO embeddings (doc_id, embedding) VALUES (?, ?)",
                (doc_id, emb_blob),
            )
            conn_thread.commit()
            logger.debug(f"Embedded {rel_path} chunk {chunk_idx} (doc_id={doc_id})")
        except Exception as e:
            logger.error(f"Error embedding {rel_path} chunk {chunk_idx}: {e}")
            stats['error_messages'].append(f"Embedding {rel_path} chunk {chunk_idx}: {str(e)}")
        finally:
            conn_thread.close()

    # Use ThreadPoolExecutor for parallel embedding
    max_workers = min(8, len(embed_tasks)) if embed_tasks else 1
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        list(pool.map(embed_worker, embed_tasks))
    
    logger.info(f"Ingestion complete: {stats['processed_files']} files, {stats['total_chunks']} chunks")
    
    return stats


def search_embeddings(
    query: str,
    db_path: str,
    model_name: str,
    top_k: int,
    provider: str = DEFAULT_PROVIDER,
) -> list:
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


def get_available_models(filter_model: Optional[str] = None) -> List[dict]:
    """
    Fetch available Ollama models using the /tags endpoint.
    Returns a list of model dictionaries with name, size, and other details.
    If filter_model is provided, returns only that model or empty list if not found.
    """
    try:
        # Try to get models from Ollama API
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = []
            for model in data.get("models", []):
                models.append(
                    {
                        "name": model["name"],
                        "size": model.get("size", 0),
                        "modified_at": model.get("modified_at", ""),
                        "digest": model.get("digest", ""),
                        "details": model.get("details", {}),
                    }
                )

            # Filter for specific model if requested
            if filter_model:
                filtered_models = [m for m in models if m["name"] == filter_model]
                if not filtered_models:
                    # If not found, create a placeholder entry
                    return [
                        {
                            "name": filter_model,
                            "size": 0,
                            "modified_at": "",
                            "digest": "",
                            "details": {},
                        }
                    ]
                return filtered_models

            return models
        else:
            logger.warning(
                f"Failed to fetch models from Ollama API: {response.status_code}"
            )
    except Exception as e:
        logger.warning(f"Error fetching models from Ollama API: {e}")

    # Fallback to custom model if provided
    if filter_model:
        return [
            {
                "name": filter_model,
                "size": 0,
                "modified_at": "",
                "digest": "",
                "details": {},
            }
        ]

    # Default fallback models
    return [
        {
            "name": "llama3.2:1b",
            "size": 0,
            "modified_at": "",
            "digest": "",
            "details": {},
        },
        {
            "name": "llama3.2:3b",
            "size": 0,
            "modified_at": "",
            "digest": "",
            "details": {},
        },
    ]


def format_model_size(size_bytes: int) -> str:
    """Format model size in human-readable format"""
    if size_bytes == 0:
        return "Unknown"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def chat(
    db: str = DEFAULT_DB_PATH,
    model: str = DEFAULT_MODEL_NAME,
    provider: str = DEFAULT_PROVIDER,
    chat_model: str = DEFAULT_CHAT_MODEL,
    topk: int = 3,
    user_input: Optional[str] = None,
    history: Optional[list] = None,
    temperature: float = 0.7,
    max_tokens: int = 512,
    top_p: float = 0.9,
    top_k: int = 40,
    repeat_penalty: float = 1.1,
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
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + history.copy()
        + [{"role": "user", "content": prompt_text}]
    )

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
                    "required": ["code"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_bash_command",
                "description": "Execute a bash command and return the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Bash command to run",
                        }
                    },
                    "required": ["command"],
                },
            },
        },
    ]

    # Prepare model options
    options = {
        "temperature": temperature,
        "num_predict": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "repeat_penalty": repeat_penalty,
    }

    try:
        # Try with tools first
        response = ollama.chat(
            model=chat_model,
            messages=messages,
            tools=tools,
            options=options,
            stream=False,
        )
    except Exception as e:
        if "does not support tools" in str(e):
            # Fallback to chat without tools
            logger.info(
                f"Model {chat_model} doesn't support tools, falling back to simple chat"
            )
            response = ollama.chat(
                model=chat_model, messages=messages, options=options, stream=False
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
                    "content": tool_result,
                }

                followup = ollama.chat(
                    model=chat_model,
                    messages=messages + [msg, tool_message],
                    options=options,
                    stream=False,
                )

                if isinstance(followup, dict):
                    followup_msg = followup.get("message", {})
                else:
                    followup_msg = (
                        followup.message if hasattr(followup, "message") else {}
                    )

                answer = (
                    followup_msg.get("content", "")
                    if isinstance(followup_msg, dict)
                    else getattr(followup_msg, "content", "")
                )
                break
        else:
            # No tool calls, just return the content
            answer = (
                msg.get("content", "")
                if isinstance(msg, dict)
                else getattr(msg, "content", "")
            )

        return (
            render_markdown_to_html(answer)
            if answer
            else "I'm sorry, I couldn't generate a response."
        )

    except Exception as e:
        logger.error(f"Error in chat function: {e}")
        return f"Error generating response: {e}"
