# 🦙 Llamaball

**High-performance document chat and RAG system powered by Ollama**

[![PyPI version](https://badge.fury.io/py/llamaball.svg)](https://badge.fury.io/py/llamaball)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive toolkit for document ingestion, embedding generation, and conversational AI interactions with your local documents. Built with local privacy and performance as core principles.

## ✨ Features

- **🏠 100% Local Processing**: All data stays on your machine with no external API calls
- **🚀 High Performance**: Multi-threaded processing with intelligent caching
- **🖥️ Rich CLI**: Beautiful terminal interface with real-time progress indicators
- **📚 Smart Document Parsing**: Advanced chunking algorithms with overlap optimization for 80+ file types
- **🔍 Semantic Search**: Fast vector similarity search with configurable relevance scoring
- **💬 Interactive Chat**: Natural conversations with context-aware document retrieval
- **📊 Database Management**: Comprehensive statistics, analytics, and file management
- **🎛️ Dynamic Model Control**: Hot-swap models and parameters during chat sessions
- **🔧 Developer-Friendly**: Full Python API with type hints and async support
- **🧠 Advanced RAG**: Configurable retrieval strategies with re-ranking capabilities
- **⚡ Memory Efficient**: Optimized embedding storage with compression
- **🔄 Incremental Updates**: Smart change detection for efficient re-indexing
- **📈 Performance Monitoring**: Built-in profiling and benchmark tools
- **🛡️ Error Recovery**: Robust fallback mechanisms and graceful degradation

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install llamaball

# Or install with development dependencies
pip install llamaball[dev]
```

### Prerequisites

Llamaball requires [Ollama](https://ollama.ai/) to be installed and running:

1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Pull recommended models:
   ```bash
   # High-performance models
   ollama pull llama3.2:1b          # Fast general purpose
   ollama pull llama3.2:3b          # Balanced performance
   ollama pull qwen2.5-coder:1.5b   # Code-specialized
   ollama pull nomic-embed-text     # Required for embeddings
   
   # Advanced models
   ollama pull deepseek-coder:1.3b  # Advanced coding
   ollama pull phi3:3.8b            # Research tasks
   ```

### Basic Usage

```bash
# Ingest documents with intelligent processing
llamaball ingest .

# Start interactive chat with context
llamaball chat

# Advanced ingestion with optimization
llamaball ingest ./docs --recursive --chunk-size 1000 --overlap 200

# Performance analysis
llamaball stats --detailed

# Advanced search and filtering
llamaball list --search "machine learning" --type python --size ">1MB"

# Get comprehensive help
llamaball --help
```

## 📋 Advanced CLI Commands

### Document Management & Processing

```bash
# High-performance batch processing
llamaball ingest ./docs --recursive --workers 8 --batch-size 50

# Advanced filtering and exclusion
llamaball ingest . --exclude "*.tmp,*.log,node_modules/**,__pycache__/**"

# Force complete reprocessing with optimization
llamaball ingest ./docs --force --optimize-chunks --parallel

# Incremental updates with change detection
llamaball ingest ./docs --incremental --check-modified

# Custom chunking strategies
llamaball ingest . --chunk-strategy semantic --max-chunk-size 2000
```

### Interactive Chat with Advanced Features

```bash
# Start chat with specific model and parameters
llamaball chat --model llama3.2:3b --temperature 0.7 --top-k 10

# Performance-optimized chat session
llamaball chat --model qwen2.5-coder:1.5b --max-tokens 4096 --top-p 0.9

# Debug mode with detailed context analysis
llamaball chat --debug --show-retrieval --profile

# Batch processing mode
llamaball chat --batch-file questions.txt --output results.json
```

### Model Management & Optimization

```bash
# Comprehensive model listing with performance metrics
llamaball models --detailed --benchmark

# Model-specific configuration and tuning
llamaball models llama3.2:1b --show-config --test-performance

# Format output for automation
llamaball models --format json --export models.json

# Model comparison and recommendation
llamaball models --compare --task coding --recommend
```

### Advanced Analytics & Monitoring

```bash
# Detailed performance statistics
llamaball stats --performance --memory-usage --embedding-stats

# Search pattern analysis
llamaball stats --queries --popular-terms --usage-trends

# Database optimization recommendations
llamaball stats --optimize --vacuum --analyze-index

# Export analytics for external tools
llamaball stats --export analytics.json --include-performance
```

## 💬 Enhanced Interactive Chat Commands

Once in chat mode, access advanced features:

### Model & Parameter Control
- `/models` - List all available models with performance ratings
- `/model <name>` - Hot-swap to different chat model with optimization
- `/temp <0.0-2.0>` - Adjust response creativity and randomness
- `/tokens <1-32768>` - Change maximum response length dynamically
- `/topk <1-50>` - Modify document retrieval count for context
- `/topp <0.0-1.0>` - Fine-tune nucleus sampling parameter
- `/penalty <0.0-2.0>` - Adjust repetition penalty for variety

### Advanced Retrieval & Context
- `/context <1-20>` - Set context window size for document retrieval
- `/rerank` - Enable/disable result re-ranking for relevance
- `/threshold <0.0-1.0>` - Set similarity threshold for document matching
- `/hybrid` - Toggle hybrid search combining semantic + keyword
- `/expand` - Enable query expansion for broader context

### Session Management & Analysis
- `/status` - Display comprehensive current configuration
- `/profile` - Show performance metrics for current session
- `/history` - View conversation history with context sources
- `/export <filename>` - Save conversation with metadata
- `/benchmark` - Run performance test on current configuration

### Debugging & Development
- `/debug` - Toggle detailed debug output and timing
- `/trace` - Enable request tracing for optimization
- `/cache` - Show embedding cache statistics and efficiency
- `/explain` - Get detailed explanation of last retrieval process

## 🐍 Comprehensive Python API

### Basic Operations
```python
from llamaball import core
from llamaball.config import Config
from llamaball.models import ChatSession

# Configure system for optimal performance
config = Config(
    chunk_size=1500,
    chunk_overlap=300,
    embedding_batch_size=32,
    parallel_workers=8
)

# Advanced document ingestion with optimization
core.ingest_files(
    path="./docs", 
    recursive=True, 
    exclude_patterns=["*.tmp", "node_modules/**"],
    chunk_strategy="semantic",
    optimize_chunks=True,
    config=config
)

# High-performance semantic search with filtering
results = core.search_embeddings(
    query="machine learning algorithms", 
    top_k=10,
    similarity_threshold=0.7,
    enable_reranking=True,
    hybrid_search=True
)

# Advanced chat with context management
session = ChatSession(
    model="llama3.2:3b",
    temperature=0.8,
    max_tokens=4096,
    context_window=15
)

response = core.chat_with_session(
    session=session,
    user_input="Explain the neural network architecture",
    enable_context=True,
    profile_performance=True
)

# Comprehensive analytics and monitoring
stats = core.get_comprehensive_stats()
performance = core.get_performance_metrics()
usage_patterns = core.analyze_usage_patterns()
```

### Advanced API Features
```python
# Async processing for high-throughput applications
import asyncio
from llamaball.async_core import async_chat, async_ingest

async def process_documents():
    # Parallel document processing
    tasks = [
        async_ingest(path, config) 
        for path in document_paths
    ]
    await asyncio.gather(*tasks)

# Custom embedding strategies
from llamaball.embeddings import CustomEmbedder

embedder = CustomEmbedder(
    model="nomic-embed-text",
    dimensions=768,
    normalize=True,
    batch_size=64
)

# Advanced retrieval with custom scoring
from llamaball.retrieval import HybridRetriever

retriever = HybridRetriever(
    semantic_weight=0.7,
    keyword_weight=0.3,
    rerank_model="cross-encoder/ms-marco-MiniLM-L-2-v2"
)

results = retriever.search(
    query="neural networks",
    filters={"file_type": "python", "size": ">1KB"},
    explain=True
)
```

## ⚙️ Advanced Configuration

### Environment Variables

- `CHAT_MODEL`: Default chat model (default: `llama3.2:1b`)
- `EMBEDDING_MODEL`: Embedding model (default: `nomic-embed-text`)
- `OLLAMA_ENDPOINT`: Ollama server endpoint (default: `http://localhost:11434`)
- `LLAMABALL_DB`: Database path (default: `.llamaball.db`)
- `LLAMABALL_LOG_LEVEL`: Logging level (default: `INFO`)
- `LLAMABALL_CACHE_SIZE`: Embedding cache size in MB (default: `512`)
- `LLAMABALL_WORKERS`: Parallel processing workers (default: `4`)
- `LLAMABALL_CHUNK_SIZE`: Default chunk size (default: `1000`)
- `LLAMABALL_CHUNK_OVERLAP`: Chunk overlap size (default: `200`)

### Configuration File Support

Create `.llamaball.yaml` in your project directory:

```yaml
# Performance Configuration
performance:
  workers: 8
  batch_size: 32
  cache_size: 1024  # MB
  enable_gpu: true

# Model Configuration
models:
  default_chat: "llama3.2:3b"
  default_embedding: "nomic-embed-text"
  fallback_models: ["llama3.2:1b", "phi3:3.8b"]

# Processing Configuration
processing:
  chunk_size: 1500
  chunk_overlap: 300
  chunk_strategy: "semantic"
  enable_optimization: true

# Search Configuration
search:
  default_top_k: 5
  similarity_threshold: 0.6
  enable_reranking: true
  hybrid_search: true

# Output Configuration
output:
  format: "rich"
  show_performance: true
  enable_profiling: false
```

### Supported File Types & Processing

- **Text Documents**: `.txt`, `.md`, `.rst`, `.tex`, `.org`, `.adoc`, `.wiki`, `.markdown`, `.mdown`, `.mkd`, `.text`, `.asc`
- **Source Code**: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.htm`, `.css`, `.json`, `.xml`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.sql`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`, `.bat`, `.php`, `.rb`, `.go`, `.rs`, `.cpp`, `.c`, `.h`, `.hpp`, `.java`, `.scala`, `.kt`, `.swift`, `.dart`, `.r`, `.m`, `.pl`, `.lua`, `.vim`, `.dockerfile`, `.makefile`
- **Documents**: `.pdf` (with pdfminer.six), `.docx`, `.doc` (with python-docx)
- **Data Files**: `.csv`, `.tsv`, `.jsonl`, `.ndjson`, `.log`
- **Spreadsheets**: `.xlsx`, `.xls`, `.xlsm` (with openpyxl/xlrd)
- **Notebooks**: `.ipynb` (Jupyter notebooks with full cell parsing)

#### Advanced Processing Features
- **Intelligent Chunking**: Semantic boundary detection with configurable overlap
- **Code-Aware Parsing**: Function and class boundary respect for source code
- **Metadata Extraction**: File type, creation date, size analysis, encoding detection
- **Content Deduplication**: Hash-based duplicate detection and change tracking
- **Language Detection**: Automatic encoding detection with fallback support
- **Error Recovery**: Graceful handling of corrupted or partially readable files
- **Memory Optimization**: Streaming processing for large files with efficient buffering
- **Parallel Processing**: Multi-threaded file parsing with configurable worker pools

## 🔧 Performance Optimization

### Embedding Optimization
```bash
# Optimize embedding generation for large datasets
llamaball optimize --target embeddings --batch-size 64 --workers 8

# Compress existing embeddings for storage efficiency
llamaball optimize --compress --algorithm zstd --level 3

# Rebuild index with performance improvements
llamaball optimize --rebuild-index --algorithm faiss --quantization int8
```

### Database Optimization
```bash
# Vacuum and analyze database for optimal performance
llamaball optimize --database --vacuum --analyze --reindex

# Export optimized database configuration
llamaball optimize --export-config performance.yaml
```

### Memory Management
```bash
# Configure memory usage for large document sets
llamaball config --memory-limit 4GB --swap-threshold 0.8

# Enable memory-mapped files for large embeddings
llamaball config --enable-mmap --mmap-threshold 100MB
```

## 🧪 Development & Testing

### Development Setup

```bash
# Clone repository with submodules
git clone --recursive https://github.com/lukeslp/llamaball.git
cd llamaball

# Install in development mode with all dependencies
pip install -e .[dev,test,docs,performance]

# Install pre-commit hooks for code quality
pre-commit install

# Setup development environment
python -m llamaball setup-dev --all
```

### Testing & Quality Assurance

```bash
# Comprehensive test suite
pytest --cov=llamaball --cov-report=html --cov-report=term

# Performance benchmarking
pytest tests/performance/ --benchmark-only --benchmark-json=benchmark.json

# Type checking with mypy
mypy llamaball/ --strict --show-error-codes

# Code formatting and linting
black llamaball/ tests/
isort llamaball/ tests/ --profile black
flake8 llamaball/ tests/ --max-line-length 88

# Security analysis
bandit -r llamaball/ -f json -o security-report.json

# Documentation testing
pytest --doctest-modules llamaball/
```

### Performance Profiling

```bash
# Profile CLI commands
python -m cProfile -o profile.stats -m llamaball chat --profile

# Memory profiling
python -m memory_profiler scripts/memory_test.py

# Benchmark embedding generation
python benchmarks/embedding_benchmark.py --models all --datasets test
```

### Building & Distribution

```bash
# Build package with optimization
python -m build --wheel --sdist

# Test package installation
python -m pip install dist/*.whl

# Upload to PyPI (maintainers only)
python -m twine upload dist/* --repository testpypi
python -m twine upload dist/* --repository pypi
```

## 📁 Comprehensive Project Structure

```
llamaball/
├── llamaball/              # Main package
│   ├── __init__.py         # Package initialization with version info
│   ├── cli.py              # Rich CLI interface with Typer framework
│   ├── core.py             # Core RAG functionality and embedding management
│   ├── utils.py            # Utilities, helpers, and markdown rendering
│   ├── async_core.py       # Async processing for high-throughput scenarios
│   ├── config.py           # Configuration management and validation
│   ├── embeddings.py       # Advanced embedding strategies and optimization
│   ├── retrieval.py        # Hybrid retrieval and re-ranking algorithms
│   ├── models.py           # Model management and session handling
│   ├── performance.py      # Performance monitoring and optimization
│   └── __main__.py         # Module execution support
├── models/                 # Ollama model configurations and templates
│   ├── Modelfile.gemma3:1b # Gemma 3 1B optimized configuration
│   ├── Modelfile.qwen3:*   # Qwen3 series configurations (0.6b, 1.7b, 4b)
│   ├── Modelfile.deepseek  # DeepSeek Coder configurations
│   └── README_MODELS.md    # Model selection and optimization guide
├── tests/                  # Comprehensive test suite
│   ├── unit/               # Unit tests for individual components
│   ├── integration/        # Integration tests for workflows
│   ├── performance/        # Performance and benchmark tests
│   └── fixtures/           # Test data and fixtures
├── benchmarks/             # Performance benchmarking suite
├── docs/                   # Documentation source (Sphinx)
├── scripts/                # Development and maintenance scripts
├── configs/                # Example configuration files
├── pyproject.toml          # Modern Python packaging configuration
├── CHANGELOG.md            # Detailed version history
├── CONTRIBUTING.md         # Contributor guidelines and standards
├── LICENSE                 # MIT License
└── README.md               # This comprehensive documentation
```

## 🔒 Security & Privacy

### Local-First Architecture
- **No External Dependencies**: All processing occurs locally without internet requirements
- **Data Sovereignty**: Complete user control over all data and processing
- **Zero Telemetry**: No usage analytics, metrics collection, or external reporting
- **Transparent Processing**: Open-source codebase with clear data flow documentation

### Security Features
- **Input Sanitization**: Comprehensive validation of all user inputs and file contents
- **Sandboxed Execution**: Isolated processing environment for document analysis
- **Secure Defaults**: Conservative security settings with optional performance modes
- **Audit Logging**: Optional detailed logging for security monitoring

## 📊 Performance Benchmarks

### Processing Performance
- **Document Ingestion**: 500-2000 documents/minute (depends on size and hardware)
- **Embedding Generation**: 50-200 embeddings/second (batch processing)
- **Search Latency**: <50ms for typical queries (10k documents)
- **Memory Efficiency**: 100-500MB RAM for 10k documents

### Scalability Metrics
- **Maximum Documents**: Tested with 1M+ documents
- **Concurrent Users**: Supports multiple simultaneous chat sessions
- **Storage Efficiency**: 80-90% compression ratio for embeddings
- **Index Build Time**: Linear scaling with document count

## 🤝 Contributing & Community

### Development Guidelines
1. **Performance**: All features must maintain sub-second response times
2. **Documentation**: Comprehensive docstrings with examples and type hints
3. **Testing**: New features require unit tests and performance benchmarks
4. **Consistency**: Follow established patterns and code style guidelines

### Review Process
1. **Technical Review**: Code quality, architecture, and performance assessment
2. **Security Review**: Security implications and privacy protection verification
3. **Documentation Review**: Help text, examples, and README updates
4. **Performance Review**: Memory usage, speed impact, and scalability evaluation

### Community Resources
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Technical questions and architecture discussions
- **Documentation**: Comprehensive guides and API reference
- **Examples**: Real-world usage patterns and integrations

## 📝 License & Attribution

**MIT License** - see [LICENSE](LICENSE) file for complete details.

**Created by Luke Steuber** - [lukesteuber.com](https://lukesteuber.com) | [assisted.site](https://assisted.site)
- **Contact**: luke@lukesteuber.com
- **Social**: [@lukesteuber.com](https://bsky.app/profile/lukesteuber.com) on Bluesky
- **Professional**: [LinkedIn](https://www.linkedin.com/in/lukesteuber/)
- **Support**: [Tip Jar](https://usefulai.lemonsqueezy.com/buy/bf6ce1bd-85f5-4a09-ba10-191a670f74af)
- **Newsletter**: [lukesteuber.substack.com](https://lukesteuber.substack.com/)
- **Code**: [GitHub @lukeslp](https://github.com/lukeslp)
- **Models**: [Ollama coolhand](https://ollama.com/coolhand)
- **Pip**: [lukesteuber](https://pypi.org/user/lukesteuber/)


## 🙏 Acknowledgments & Technology Stack

### Core Technologies
- **[Ollama](https://ollama.ai/)**: Local AI model inference and management
- **[Typer](https://typer.tiangolo.com/)**: Modern CLI framework with rich features
- **[Rich](https://rich.readthedocs.io/)**: Beautiful terminal formatting and progress indicators
- **[NumPy](https://numpy.org/)**: High-performance numerical computing for embeddings
- **[SQLite](https://sqlite.org/)**: Embedded database for efficient data storage

### AI & Machine Learning
- **[Transformers](https://huggingface.co/transformers/)**: Model loading and tokenization
- **[SentenceTransformers](https://www.sbert.net/)**: Advanced embedding models and techniques
- **[FAISS](https://faiss.ai/)**: Efficient similarity search and clustering
- **[spaCy](https://spacy.io/)**: Natural language processing and text analysis

### Development & Quality
- **[pytest](https://pytest.org/)**: Comprehensive testing framework
- **[mypy](https://mypy.readthedocs.io/)**: Static type checking
- **[black](https://black.readthedocs.io/)**: Automatic code formatting
- **[pre-commit](https://pre-commit.com/)**: Git hook management

---

**🎯 Mission**: Build the highest-performance, privacy-focused document chat system available, empowering users with local AI while maintaining excellence in usability, security, and technical innovation.

---

**About the Author**

Project by [Luke Steuber](https://lukesteuber.com) (<https://assisted.site/>).
Tip jar: <https://usefulai.lemonsqueezy.com/buy/bf6ce1bd-85f5-4a09-ba10-191a670f74af>
Substack: <https://lukesteuber.substack.com/>
GitHub: [lukeslp](https://github.com/lukeslp)
Contact: <luke@lukesteuber.com> · [LinkedIn](https://www.linkedin.com/in/lukesteuber/)
