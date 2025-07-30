# 🦙 llamaball

**Accessible, ethical, and actually useful document chat and RAG system powered by Ollama.**

## ✨ Features

- **🏠 100% Local**: All processing happens on your machine - no data leaves your computer
- **♿ Accessibility First**: Screen-reader friendly output, clear navigation, semantic markup
- **🖥️  Interactive CLI**: Beautiful, intuitive command-line interface with rich formatting
- **📚 Smart Document Parsing**: Supports .txt, .md, .py, .json, .csv files with intelligent chunking
- **🔍 Semantic Search**: Fast vector similarity search using local embeddings
- **💬 Interactive Chat**: Natural language conversations with your documents
- **🛠️  Function Calling**: Tool execution and code running capabilities
- **📊 Rich Statistics**: Detailed database insights and file management
- **🎨 Markdown Rendering**: Beautiful terminal output with proper formatting

## 📦 Installation

```bash
# Install in development mode (recommended)
git clone <repository>
cd llamaball
pip install -e .

# Or install from source
pip install .
```

### Dependencies
- Python 3.8+
- Ollama (for local LLM inference)
- Required Python packages (auto-installed): typer, rich, ollama, numpy, tiktoken, prompt_toolkit, markdown-it-py, tqdm

## 🚀 Quick Start

1. **Ingest your documents:**
   ```bash
   llamaball ingest .
   ```

2. **Start chatting:**
   ```bash
   llamaball chat
   ```

3. **Ask questions about your documents!**

## 📋 CLI Commands

### 🏠 Main Commands

| Command | Short | Description | Example |
|---------|-------|-------------|---------|
| `llamaball` | | Show welcome and help | `llamaball` |
| `llamaball --help` | `-h` | Show detailed help | `llamaball -h` |
| `llamaball --version` | `-v` | Show version info | `llamaball -v` |

### 📚 Document Management

#### `llamaball ingest [DIRECTORY]`
Ingest documents and build embeddings database.

**Arguments:**
- `DIRECTORY` - Directory to ingest (default: current directory)

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--model` | `-m` | Embedding model name | `nomic-embed-text:latest` |
| `--provider` | `-p` | Provider (ollama/openai) | `ollama` |
| `--recursive` | `-r` | Recursively scan subdirectories | `False` |
| `--exclude` | `-e` | Exclude patterns (comma-separated) | `` |
| `--force` | `-f` | Force re-indexing of all files | `False` |
| `--quiet` | `-q` | Suppress progress output | `False` |

**Examples:**
```bash
llamaball ingest                    # Ingest current directory
llamaball ingest ./docs -r          # Recursively ingest docs/
llamaball ingest ~/papers -m qwen3  # Use different model
llamaball ingest . -e "*.log,temp*" # Exclude patterns
llamaball ingest /path/to/docs -f   # Force re-indexing
```

### 💬 Chat Interface

#### `llamaball chat`
Start interactive chat with your documents.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--model` | `-m` | Embedding model | `nomic-embed-text:latest` |
| `--provider` | `-p` | Provider (ollama/openai) | `ollama` |
| `--chat-model` | `-c` | Chat model name | `llama3.2:1b` |
| `--top-k` | `-k` | Number of relevant docs to retrieve | `3` |
| `--temperature` | `-t` | Chat model temperature (0.0-2.0) | `0.7` |
| `--max-tokens` | `-T` | Maximum tokens in response | `512` |
| `--system` | `-s` | Custom system prompt | `None` |
| `--debug` | | Show debug information | `False` |

**Examples:**
```bash
llamaball chat                           # Basic chat
llamaball chat -c qwen3:4b               # Use specific chat model
llamaball chat -k 5 -t 0.3               # More docs, lower temperature
llamaball chat -s "Be concise"           # Custom system prompt
llamaball chat --debug                   # Show debug info
```

**Chat Commands:**
- `exit`, `quit`, `q` - End the session
- `help` - Show chat help
- `stats` - Show database statistics  
- `clear` - Clear conversation history

### 📊 Database Management

#### `llamaball stats`
Show database statistics and information.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--verbose` | `-v` | Show detailed statistics | `False` |
| `--format` | `-f` | Output format: table, json, plain | `table` |

**Examples:**
```bash
llamaball stats                    # Basic statistics
llamaball stats -v                 # Detailed statistics  
llamaball stats -f json            # JSON output
llamaball stats -f plain           # Plain text output
```

#### `llamaball list`
List all files in the database.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--filter` | `-f` | Filter files by pattern | `` |
| `--sort` | `-s` | Sort by: name, date, size | `name` |
| `--limit` | `-l` | Limit results (0 = no limit) | `0` |

**Examples:**
```bash
llamaball list                     # List all files
llamaball list -f "*.py"           # List Python files only
llamaball list -s date             # Sort by modification date
llamaball list -l 10               # Show only first 10 files
```

#### `llamaball clear`
Clear the database (delete all data).

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--force` | `-f` | Skip confirmation prompt | `False` |
| `--backup/--no-backup` | `-b` | Create backup before clearing | `True` |

**Examples:**
```bash
llamaball clear                    # Clear with confirmation
llamaball clear -f                 # Clear without confirmation
llamaball clear --no-backup        # Clear without backup
```

## 🐍 Python API Usage

```python
from llamaball import core

# Ingest files
core.ingest_files(
    directory=".",
    db_path=".llamaball.db",
    model_name="nomic-embed-text:latest",
    provider="ollama",
    recursive=True
)

# Search embeddings
results = core.search_embeddings(
    db_path=".llamaball.db",
    query="your search query",
    model_name="nomic-embed-text:latest",
    provider="ollama",
    top_k=5
)

# Chat with documents
response = core.chat(
    db_path=".llamaball.db",
    embed_model="nomic-embed-text:latest",
    provider="ollama",
    chat_model="llama3.2:1b",
    top_k=3,
    user_input="your question",
    conversation_history=[]
)
```

## ♿ Accessibility Features

- **Screen Reader Support**: All output uses semantic markup and clear structure
- **Keyboard Navigation**: Full functionality available via keyboard
- **High Contrast**: Rich terminal formatting with good color contrast
- **Clear Error Messages**: Descriptive error messages with suggested solutions
- **Progress Indicators**: Clear feedback during long operations
- **Consistent Layout**: Predictable command structure and output format

## 🔧 Configuration

### Environment Variables
- `CHAT_MODEL`: Default chat model (default: `llama3.2:1b`)
- `OLLAMA_ENDPOINT`: Ollama server endpoint (default: `http://localhost:11434`)

### Supported File Types
- **Text**: `.txt`, `.md`
- **Code**: `.py`, `.js`, `.html`, `.css`
- **Data**: `.json`, `.csv`
- **More formats can be added via the core API**

## 🛠️  Development

### Project Structure
```
llamaball/
├── __init__.py          # Package initialization
├── cli.py              # CLI interface (Typer app)
├── core.py             # Core logic (embedding, search, chat)
├── utils.py            # Utilities (markdown rendering, etc.)
└── README.md           # This file
```

### Adding New Features
1. Core functionality goes in `core.py`
2. CLI commands go in `cli.py`
3. Utility functions go in `utils.py`
4. Always include docstrings and type hints
5. Maintain accessibility standards

## 🤝 Contributing

1. Follow accessibility-first design principles
2. Include comprehensive docstrings
3. Use type hints throughout
4. Test with screen readers when possible
5. Maintain consistent CLI patterns

## 📄 License

MIT License - Built with ❤️ for accessibility and local AI.

## 🙏 Credits

- Built on [Ollama](https://ollama.ai) for local LLM inference
- Uses [Typer](https://typer.tiangolo.com/) for CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Designed with accessibility and maintainability as core principles 