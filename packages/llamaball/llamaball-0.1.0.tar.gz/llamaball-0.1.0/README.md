# 🦙 Doc Chat AI (Llamaball)

**Accessible document chat and RAG system powered by Ollama**

A comprehensive toolkit for document ingestion, embedding generation, and conversational AI interactions with your local documents. Built with accessibility and local privacy as core principles.

## 🚀 Quick Start with Llamaball

**The project has been packaged as `llamaball` - an installable CLI and Python library:**

```bash
# Install the package
pip install -e .

# Ingest documents
llamaball ingest .

# Start chatting
llamaball chat
```

## 📦 What's Included

### 🦙 Llamaball Package (`llamaball/`)
- **Interactive CLI** with rich formatting and accessibility features
- **Python API** for programmatic use
- **Comprehensive documentation** with all flags and examples
- **Screen reader friendly** output and navigation

### 🛠️ Setup Scripts
- `quick-setup.sh` - Automated model downloads and configuration
- `start-rag-system.sh` - System startup
- `stop-rag-system.sh` - Clean shutdown
- `test-rag-system.sh` - Integration testing

### 📋 Model Configurations (`models/`)
- `Modelfile.gemma3:1b` - Gemma 3 1B configuration
- `Modelfile.qwen3:0.6b` - Qwen3 0.6B configuration  
- `Modelfile.qwen3:1.7b` - Qwen3 1.7B configuration
- `Modelfile.qwen3:4b` - Qwen3 4B configuration

### 🐍 Legacy Scripts (Transitioning)
- `doc_chat_ollama.py` - Original Ollama implementation (now in `llamaball.core`)
- `doc_chat_openai.py` - OpenAI implementation

## 🎯 Features

- **🏠 100% Local Processing**: All data stays on your machine
- **♿ Accessibility First**: Screen reader support, keyboard navigation, clear structure
- **🖥️ Rich CLI**: Beautiful terminal interface with progress indicators
- **📚 Smart Document Parsing**: Intelligent chunking for optimal embeddings
- **🔍 Semantic Search**: Fast vector similarity search
- **💬 Interactive Chat**: Natural conversations with your documents
- **📊 Database Management**: Comprehensive statistics and file management

## 📋 CLI Commands

See the complete documentation in `llamaball/README.md` or run:

```bash
llamaball --help              # Main help
llamaball ingest --help       # Ingestion options
llamaball chat --help         # Chat configuration
llamaball stats --help        # Database statistics
```

## 🔧 Development Setup

```bash
# Clone and install
git clone <repository>
cd doc_chat_ai
pip install -e .

# Run setup (optional - for Ollama models)
./quick-setup.sh

# Start using llamaball
llamaball ingest .
llamaball chat
```

## 🐍 Python API Usage

```python
from llamaball import core

# Ingest documents
core.ingest_files("./docs", recursive=True)

# Search embeddings  
results = core.search_embeddings(query="search term", top_k=5)

# Chat with documents
response = core.chat(user_input="What is this about?", history=[])
```

## 🎛️ Configuration

### Environment Variables
- `CHAT_MODEL`: Default chat model (default: `llama3.2:1b`)
- `OLLAMA_ENDPOINT`: Ollama server endpoint

### Supported File Types
- Text: `.txt`, `.md`
- Code: `.py`, `.js`, `.html`, `.css`  
- Data: `.json`, `.csv`

## ♿ Accessibility Features

- **Screen Reader Support**: Semantic markup and clear structure
- **Keyboard Navigation**: Full CLI functionality via keyboard
- **High Contrast Output**: Rich terminal formatting with good contrast
- **Clear Error Messages**: Descriptive feedback with suggested solutions
- **Progress Indicators**: Real-time feedback during operations
- **Consistent Layout**: Predictable command structure

## 📁 Project Structure

```
doc_chat_ai/
├── llamaball/              # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI interface  
│   ├── core.py            # Core functionality
│   ├── utils.py           # Utilities
│   └── README.md          # Package documentation
├── models/                # Model configurations
├── configs/               # Configuration files
├── scripts/               # Utility scripts
├── setup.py               # Package installation
└── README.md              # This file
```

## 🤝 Contributing

1. Follow accessibility-first design principles
2. Include comprehensive docstrings and type hints
3. Test with screen readers when possible
4. Maintain consistent CLI patterns
5. Update documentation for all changes

## 📄 License

MIT License - Built with ❤️ for accessibility and local AI.
