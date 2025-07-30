# 🦙 llamaball

**Accessible, ethical, and actually useful document chat and RAG system powered by Ollama.**

## ✨ Features

- **🏠 100% Local**: All processing happens on your machine - no data leaves your computer
- **♿ Accessibility First**: Screen-reader friendly output, clear navigation, semantic markup
- **🖥️ Interactive CLI**: Beautiful, intuitive command-line interface with rich formatting and progress bars
- **📚 Smart Document Parsing**: Supports 100+ file types with intelligent chunking and content extraction
- **🔍 Semantic Search**: Fast vector similarity search using local embeddings
- **💬 Interactive Chat**: Natural language conversations with your documents
- **🛠️ Function Calling**: Tool execution and code running capabilities  
- **📊 Rich Statistics**: Detailed database insights and file management with beautiful visualizations
- **🎨 Enhanced UI**: Rich colors, progress bars, and beautiful terminal formatting throughout

## 📦 Installation

```bash
# Install in development mode (recommended)
git clone <repository>
cd llamaball
pip install -e .

# Or install from source
pip install .

# Install with all optional dependencies for maximum file support
pip install -e ".[files]"
```

### Dependencies
- **Core**: Python 3.8+, Ollama, typer, rich, ollama, numpy, tiktoken, prompt_toolkit
- **Optional**: beautifulsoup4 (HTML), pdfminer.six (PDF), python-docx (Word), openpyxl (Excel), pypandoc (RTF)

## 🗂️ Comprehensive File Type Support

Llamaball supports **100+ file types** across 10 categories:

### 📝 Text Documents
`.txt`, `.md`, `.rst`, `.tex`, `.org`, `.adoc`, `.wiki`, `.markdown`, `.mdown`, `.mkd`, `.text`, `.asc`, `.rtf`, `.textile`, `.mediawiki`, `.creole`, `.bbcode`

### 💻 Source Code  
`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.htm`, `.css`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.sql`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`, `.bat`, `.php`, `.rb`, `.go`, `.rs`, `.cpp`, `.c`, `.h`, `.hpp`, `.java`, `.scala`, `.kt`, `.swift`, `.dart`, `.r`, `.m`, `.pl`, `.lua`, `.vim`, `.dockerfile`, `.makefile`, `.gradle`, `.cmake`, `.scss`, `.sass`, `.less`, `.styl`, `.vue`, `.svelte`, `.astro`, `.mjs`, `.cjs`, `.coffee`, `.litcoffee`

### 🌐 Web Files
`.html`, `.htm`, `.xhtml`, `.xml`, `.rss`, `.atom`, `.svg`, `.wml`, `.xsl`, `.xslt`, `.jsp`, `.asp`, `.aspx`, `.php`

### 📄 Documents
`.pdf`, `.docx`, `.doc`, `.odt`, `.pages`, `.rtf`

### 📊 Data Files
`.csv`, `.tsv`, `.jsonl`, `.ndjson`, `.log`, `.parquet`, `.arrow`, `.feather`, `.pickle`, `.pkl`, `.hdf5`, `.h5`

### 📈 Spreadsheets
`.xlsx`, `.xls`, `.xlsm`, `.ods`, `.numbers`, `.gnumeric`

### 📓 Notebooks
`.ipynb`, `.rmd`, `.qmd`, `.rmarkdown`

### 📧 Email
`.eml`, `.msg`, `.mbox`, `.maildir`

### 🗜️ Archives
`.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2`, `.tar.xz`, `.txz`, `.rar`, `.7z`

### ⚙️ Configuration
`.conf`, `.config`, `.properties`, `.env`, `.editorconfig`, `.gitignore`, `.dockerignore`, `.eslintrc`, `.prettierrc`, `.babelrc`, `.tsconfig`, `.package`, `.lock`

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
Ingest documents and build embeddings database with beautiful progress tracking.

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
| `--show-types` | `-t` | Show supported file types tree | `False` |

**Examples:**
```bash
llamaball ingest                    # Ingest current directory
llamaball ingest ./docs -r          # Recursively ingest docs/
llamaball ingest ~/papers -m qwen3  # Use different model
llamaball ingest . -e "*.log,temp*" # Exclude patterns
llamaball ingest /path/to/docs -f   # Force re-indexing
llamaball ingest --show-types       # Beautiful file type tree
```

### 💬 Chat Interface

#### `llamaball chat`
Start interactive chat with beautiful styling and enhanced features.

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
llamaball chat                           # Basic chat with beautiful UI
llamaball chat -c qwen3:4b               # Use specific chat model
llamaball chat -k 5 -t 0.3               # More docs, lower temperature
llamaball chat -s "Be concise"           # Custom system prompt
llamaball chat --debug                   # Show debug info
```

**Enhanced Chat Commands:**
- `exit`, `quit`, `q` - End the session with styled goodbye
- `help` - Show beautiful help panel
- `stats` - Show database statistics in styled panel
- `clear` - Clear conversation history
- `/models` - List available models in table
- `/model [name]` - Switch chat model
- `/temp [0.0-2.0]` - Change temperature
- `/tokens [1-8192]` - Change max tokens
- `/topk [1-20]` - Change document retrieval count
- `/status` - Show current settings
- `/commands` - Show all available commands

### 📊 Database Management

#### `llamaball stats`
Show enhanced database statistics with beautiful tables.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--verbose` | `-v` | Show detailed statistics | `False` |
| `--format` | `-f` | Output format: table, json, plain | `table` |

**Examples:**
```bash
llamaball stats                    # Beautiful statistics table
llamaball stats -v                 # Detailed statistics with file types
llamaball stats -f json            # JSON output
llamaball stats -f plain           # Plain text output
```

#### `llamaball list`
List all files with enhanced table display.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--filter` | `-f` | Filter files by pattern | `` |
| `--sort` | `-s` | Sort by: name, date, size | `name` |
| `--limit` | `-l` | Limit results (0 = no limit) | `0` |

**Examples:**
```bash
llamaball list                     # List all files with icons
llamaball list -f "*.py"           # List Python files only
llamaball list -s date             # Sort by modification date
llamaball list -l 10               # Show only first 10 files
```

#### `llamaball clear`
Clear the database with styled confirmations.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--database` | `-d` | SQLite database path | `.llamaball.db` |
| `--force` | `-f` | Skip confirmation prompt | `False` |
| `--backup/--no-backup` | `-b` | Create backup before clearing | `True` |

#### `llamaball models`
List available models with enhanced styling.

**Options:**
| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--format` | `-f` | Output format: table, json, plain | `table` |

**Examples:**
```bash
llamaball models                   # Beautiful models table
llamaball models llama3.2:1b       # Show specific model details
llamaball models --format json     # JSON output
```

## 🎨 Enhanced UI Features

### 🌈 Rich Colors & Styling
- **Primary**: Teal (`#00D4AA`) - Main branding and highlights
- **Success**: Green (`#00C851`) - Successful operations  
- **Warning**: Orange (`#FFB84D`) - Warnings and notes
- **Error**: Red (`#FF4444`) - Errors and failures
- **Info**: Light Blue (`#33B5E5`) - Information and tips
- **Accent**: Purple (`#9C27B0`) - Special highlights
- **Muted**: Gray (`#6C757D`) - Secondary text

### 📊 Progress Indicators
- **File Scanning**: Animated spinner with file count
- **Document Processing**: Progress bar with current file name
- **Embedding Generation**: Multi-threaded progress tracking
- **Real-time Updates**: Live progress with time estimates

### 🎭 Interactive Elements
- **Gradient Text**: Beautiful title animations
- **Styled Panels**: Bordered content areas with consistent theming
- **Rich Tables**: Enhanced tables with proper column styling
- **Tree Views**: Hierarchical file type displays
- **Status Indicators**: Contextual status messages throughout

### ♿ Accessibility Features
- **Screen Reader Support**: All output uses semantic markup and clear structure
- **Keyboard Navigation**: Full functionality available via keyboard  
- **High Contrast**: Rich terminal formatting with good color contrast
- **Clear Error Messages**: Descriptive error messages with suggested solutions
- **Progress Feedback**: Clear visual and textual feedback during operations
- **Consistent Layout**: Predictable command structure and output format

## 🐍 Python API Usage

```python
from llamaball import core

# Ingest files with progress callback
def my_progress(current, total, filename):
    print(f"Processing {current}/{total}: {filename}")

core.ingest_files(
    directory=".",
    db_path=".llamaball.db",
    model_name="nomic-embed-text:latest",
    provider="ollama",
    recursive=True,
    progress_callback=my_progress
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

## 🔧 Configuration

### Environment Variables
- `CHAT_MODEL`: Default chat model (default: `llama3.2:1b`)
- `OLLAMA_ENDPOINT`: Ollama server endpoint (default: `http://localhost:11434`)

### Advanced Parsing Features
- **Intelligent Chunking**: Semantic boundary detection with configurable overlap
- **Code-Aware Parsing**: Function and class boundary respect for source code
- **Metadata Extraction**: File type, creation date, size analysis, encoding detection
- **Content Deduplication**: Hash-based duplicate detection and change tracking
- **Language Detection**: Automatic encoding detection with fallback support
- **Error Recovery**: Graceful handling of corrupted or partially readable files
- **Memory Optimization**: Streaming processing for large files with efficient buffering
- **Parallel Processing**: Multi-threaded file parsing with configurable worker pools

## 🛠️ Development

### Project Structure
```
llamaball/
├── __init__.py          # Package initialization with enhanced exports
├── cli.py              # Beautiful CLI interface with rich styling
├── core.py             # Enhanced core logic with progress tracking
├── parsers.py          # Comprehensive file parsers (100+ formats)
├── utils.py            # Utilities including markdown rendering
└── README.md           # This comprehensive documentation
```

### Adding New Features
1. Core functionality goes in `core.py`
2. CLI commands go in `cli.py` with rich styling
3. File parsers go in `parsers.py` with proper error handling
4. Utility functions go in `utils.py`
5. Always include docstrings and type hints
6. Maintain accessibility standards
7. Use consistent color theming from `THEME_COLORS`

## 🤝 Contributing

1. Follow accessibility-first design principles
2. Include comprehensive docstrings
3. Use type hints throughout
4. Test with screen readers when possible
5. Maintain consistent CLI patterns
6. Use rich styling and progress indicators
7. Ensure all file types have proper error handling

## 📄 License

MIT License - Built with ❤️ for accessibility and local AI.

## 🙏 Credits

- Built on [Ollama](https://ollama.ai) for local LLM inference
- Uses [Typer](https://typer.tiangolo.com/) for CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Designed with accessibility and maintainability as core principles
- Enhanced with comprehensive file parsing and progress tracking
- Styled with beautiful colors and animations throughout 