#!/usr/bin/env python3
"""
Llamaball CLI - Accessible document chat and RAG system
File Purpose: Interactive command-line interface for llamaball
Primary Functions: ingest, chat, stats, list-files, clear-db
Inputs: CLI arguments and interactive prompts
Outputs: Formatted terminal output with accessibility features
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import core

# Initialize rich console for better output
console = Console()

# Main app with comprehensive help
app = typer.Typer(
    name="llamaball",
    help="""
🦙 Llamaball: Accessible Document Chat & RAG System

An ethical, accessible, and actually useful document chat system powered by Ollama.
Perfect for researchers, developers, and anyone who needs to chat with their documents.

Features:
• Local AI processing (no data leaves your machine)
• Accessibility-first design (screen reader friendly)
• Fast semantic search and retrieval
• Function calling and tool execution
• Multiple model support

Examples:
  llamaball models                      # List available models
  llamaball ingest .                    # Ingest current directory
  llamaball ingest ~/docs -r            # Recursively ingest docs folder
  llamaball chat                        # Start interactive chat
  llamaball chat -c llamaball-qwen3:4b  # Chat with specific model
  llamaball chat --temp 0.3 --max-tokens 1024  # Adjust parameters
  llamaball stats                       # Show database statistics
  
Get started:
  1. llamaball ingest --dir /path/to/docs
  2. llamaball chat
  3. Ask questions about your documents!
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


def show_welcome():
    """Display welcome message with ASCII art and quick start info"""
    welcome_text = """
[bold green]🦙 Welcome to Llamaball![/bold green]
[italic]Accessible, ethical, actually useful document chat[/italic]

[bold]Quick Start:[/bold]
• [cyan]llamaball ingest .[/cyan] - Index current directory
• [cyan]llamaball chat[/cyan] - Start chatting with your docs
• [cyan]llamaball --help[/cyan] - Show detailed help

[bold]Need help?[/bold] All commands support [cyan]--help[/cyan] flag
"""
    console.print(Panel(welcome_text, title="Llamaball", border_style="green"))


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version information"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-V", help="Enable verbose logging"
    ),
):
    """
    Llamaball: Accessible document chat and RAG system powered by Ollama.

    Run without arguments to see this help, or use specific commands below.
    """
    if version:
        console.print(f"[bold]Llamaball[/bold] version [green]0.1.0[/green]")
        console.print("Built with ❤️  for accessibility and local AI")
        raise typer.Exit()

    if verbose:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)
        console.print("[dim]Verbose logging enabled[/dim]")


@app.command(name="ingest")
def ingest_command(
    directory: Optional[str] = typer.Argument(
        None, help="Directory to ingest (default: current directory)"
    ),
    db: str = typer.Option(
        core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"
    ),
    model: str = typer.Option(
        core.DEFAULT_MODEL_NAME, "--model", "-m", help="Embedding model name"
    ),
    provider: str = typer.Option(
        core.DEFAULT_PROVIDER, "--provider", "-p", help="Provider: ollama or openai"
    ),
    recursive: bool = typer.Option(
        False, "--recursive", "-r", help="Recursively ingest subdirectories"
    ),
    exclude: str = typer.Option(
        "", "--exclude", "-e", help="Exclude patterns (comma-separated)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force re-indexing of all files"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
    show_types: bool = typer.Option(
        False, "--show-types", "-t", help="Show supported file types and exit"
    ),
):
    """
    📚 Ingest documents and build embeddings database.

    This command scans the specified directory, extracts text from supported files,
    chunks the content intelligently, and creates embeddings for semantic search.

    Supported file types include:
    • Text: .txt, .md, .rst, .tex, .org, .wiki, etc.
    • Code: .py, .js, .ts, .html, .css, .json, .yaml, .sql, etc.
    • Documents: .pdf, .docx, .doc
    • Data: .csv, .tsv, .xlsx, .xls, .jsonl
    • Spreadsheets: .xlsx, .xls, .ods
    • Notebooks: .ipynb (Jupyter notebooks)

    Examples:
      llamaball ingest                    # Ingest current directory
      llamaball ingest ./docs -r          # Recursively ingest docs/
      llamaball ingest ~/papers -m qwen3  # Use different model
      llamaball ingest . --exclude "*.log,temp*"  # Exclude patterns
      llamaball ingest --show-types       # Show all supported file types
    """
    # Show supported file types if requested
    if show_types:
        from .parsers import FileParser
        parser = FileParser()
        
        console.print("[bold]🗂️  Supported File Types:[/bold]\n")
        
        # Create table of supported types
        table = Table(title="File Type Support", show_header=True, header_style="bold magenta")
        table.add_column("Category", style="cyan", width=12)
        table.add_column("Extensions", style="green")
        table.add_column("Description", style="dim")
        
        categories = [
            ("Text", parser.TEXT_EXTENSIONS, "Plain text, markdown, documentation"),
            ("Code", parser.CODE_EXTENSIONS, "Source code, configuration files"),
            ("Documents", parser.DOCUMENT_EXTENSIONS, "PDF, Word documents"),
            ("Data", parser.DATA_EXTENSIONS, "CSV, TSV, JSON lines"),
            ("Spreadsheets", parser.SPREADSHEET_EXTENSIONS, "Excel, OpenDocument"),
            ("Notebooks", parser.NOTEBOOK_EXTENSIONS, "Jupyter notebooks"),
        ]
        
        for category, extensions, description in categories:
            ext_list = ", ".join(sorted(extensions))
            if len(ext_list) > 60:
                ext_list = ext_list[:57] + "..."
            table.add_row(category, ext_list, description)
        
        console.print(table)
        
        total_types = sum(len(exts) for _, exts, _ in categories)
        console.print(f"\n[bold green]Total supported file types: {total_types}[/bold green]")
        return

    # Use current directory if none specified
    if directory is None:
        directory = "."

    # Validate directory exists
    dir_path = Path(directory)
    if not dir_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Directory '{directory}' does not exist"
        )
        raise typer.Exit(1)

    if not dir_path.is_dir():
        console.print(f"[bold red]Error:[/bold red] '{directory}' is not a directory")
        raise typer.Exit(1)

    # Interactive confirmation for recursive mode
    if not recursive and not quiet:
        recursive = typer.confirm(
            f"📁 Recursively scan subdirectories in '{directory}'?", default=False
        )

    # Parse exclude patterns
    exclude_patterns = (
        [p.strip() for p in exclude.split(",") if p.strip()] if exclude else []
    )

    # Show what we're about to do
    if not quiet:
        console.print(f"\n[bold]Ingestion Configuration:[/bold]")
        console.print(f"📂 Directory: [cyan]{directory}[/cyan]")
        console.print(f"🗄️  Database: [cyan]{db}[/cyan]")
        console.print(f"🤖 Model: [cyan]{model}[/cyan]")
        console.print(f"🔄 Recursive: [cyan]{recursive}[/cyan]")
        console.print(f"⚡ Force reindex: [cyan]{force}[/cyan]")
        console.print(f"🚫 Exclude: [cyan]{exclude if exclude else 'none'}[/cyan]")
        console.print()

    try:
        if not quiet:
            with console.status("🔍 Processing documents..."):
                stats = core.ingest_files(
                    directory, db, model, provider, recursive, exclude_patterns, force
                )
        else:
            stats = core.ingest_files(
                directory, db, model, provider, recursive, exclude_patterns, force
            )

        if not quiet:
            console.print(
                "[bold green]✅ Ingestion completed successfully![/bold green]"
            )
            
            # Show comprehensive statistics
            console.print(f"\n[bold]📊 Ingestion Results:[/bold]")
            console.print(f"✅ Processed: [green]{stats['processed_files']}[/green] files")
            console.print(f"⏭️  Skipped: [yellow]{stats['skipped_files']}[/yellow] files")
            console.print(f"❌ Errors: [red]{stats['error_files']}[/red] files")
            console.print(f"📄 Total chunks: [cyan]{stats['total_chunks']}[/cyan]")
            
            if stats['processed_extensions']:
                console.print(f"🗂️  File types: [dim]{', '.join(sorted(stats['processed_extensions']))}[/dim]")
            
            if stats['error_files'] > 0:
                console.print(f"\n[bold yellow]⚠️  Issues Encountered:[/bold yellow]")
                
                # Categorize errors for better display
                dependency_errors = []
                corruption_errors = []
                protection_errors = []
                other_errors = []
                
                for error in stats['error_messages']:
                    if "not available" in error and "Install with:" in error:
                        dependency_errors.append(error)
                    elif "corrupted" in error or "not a valid" in error:
                        corruption_errors.append(error)
                    elif "password protected" in error or "encrypted" in error:
                        protection_errors.append(error)
                    else:
                        other_errors.append(error)
                
                if dependency_errors:
                    console.print(f"[bold blue]📦 Missing Dependencies ({len(dependency_errors)} files):[/bold blue]")
                    console.print("  To enable these file types, install: [cyan]pip install llamaball[files][/cyan]")
                    for error in dependency_errors[:3]:  # Show first 3
                        file_name = error.split(":")[0]
                        console.print(f"  • {file_name}")
                    if len(dependency_errors) > 3:
                        console.print(f"  ... and {len(dependency_errors) - 3} more files")
                
                if corruption_errors:
                    console.print(f"[bold red]🗂️  Corrupted Files ({len(corruption_errors)} files):[/bold red]")
                    for error in corruption_errors[:3]:
                        console.print(f"  • {error}")
                    if len(corruption_errors) > 3:
                        console.print(f"  ... and {len(corruption_errors) - 3} more files")
                
                if protection_errors:
                    console.print(f"[bold yellow]🔒 Protected Files ({len(protection_errors)} files):[/bold yellow]")
                    for error in protection_errors[:3]:
                        console.print(f"  • {error}")
                    if len(protection_errors) > 3:
                        console.print(f"  ... and {len(protection_errors) - 3} more files")
                
                if other_errors:
                    console.print(f"[bold red]❌ Other Errors ({len(other_errors)} files):[/bold red]")
                    for error in other_errors[:3]:
                        console.print(f"  • {error}")
                    if len(other_errors) > 3:
                        console.print(f"  ... and {len(other_errors) - 3} more files")

    except Exception as e:
        console.print(f"[bold red]❌ Ingestion failed:[/bold red] {e}")
        if not quiet:  # Show traceback in non-quiet mode instead of verbose
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


@app.command(name="chat")
def chat_command(
    db: str = typer.Option(
        core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"
    ),
    model: str = typer.Option(
        core.DEFAULT_MODEL_NAME, "--model", "-m", help="Embedding model"
    ),
    provider: str = typer.Option(
        core.DEFAULT_PROVIDER, "--provider", "-p", help="Provider: ollama or openai"
    ),
    chat_model: str = typer.Option(
        core.DEFAULT_CHAT_MODEL, "--chat-model", "-c", help="Chat model name"
    ),
    topk: int = typer.Option(
        3, "--top-k", "-k", help="Number of relevant documents to retrieve"
    ),
    temperature: float = typer.Option(
        0.7, "--temperature", "-t", help="Chat model temperature (0.0-2.0)"
    ),
    max_tokens: int = typer.Option(
        512, "--max-tokens", "-T", help="Maximum tokens in response"
    ),
    top_p: float = typer.Option(
        0.9, "--top-p", help="Top-P nucleus sampling (0.0-1.0)"
    ),
    top_k: int = typer.Option(40, "--top-k-sampling", help="Top-K sampling parameter"),
    repeat_penalty: float = typer.Option(
        1.1, "--repeat-penalty", help="Repetition penalty (0.0-2.0)"
    ),
    system_prompt: Optional[str] = typer.Option(
        None, "--system", "-s", help="Custom system prompt"
    ),
    list_models: bool = typer.Option(
        False, "--list-models", "-l", help="List available models and exit"
    ),
    debug: bool = typer.Option(False, "--debug", help="Show debug information"),
):
    """
    💬 Start interactive chat with your documents.

    This command launches an interactive chat session where you can ask questions
    about your ingested documents. The system will find relevant content and
    generate contextual responses.

    Chat Features:
    • Semantic search across your documents
    • Function calling and tool execution
    • Markdown rendering in terminal
    • Screen reader friendly output
    • Conversation history

    Commands during chat:
    • 'exit' or 'quit' - End the session
    • 'help' - Show chat help
    • 'stats' - Show database statistics
    • 'clear' - Clear conversation history

    Examples:
      llamaball chat --list-models             # List available models
      llamaball chat                           # Basic chat
      llamaball chat -c llamaball-qwen3:4b     # Use specific chat model
      llamaball chat --top-k 5 --temp 0.3     # More documents, lower temperature
      llamaball chat --system "Be concise"    # Custom system prompt
      llamaball chat --top-p 0.8 --repeat-penalty 1.2  # Advanced parameters
    """

    # Handle list models option
    if list_models:
        console.print("[bold]🤖 Available Chat Models:[/bold]\n")
        list_available_models()
        return
    # Check if database exists
    db_path = Path(db)
    if not db_path.exists():
        console.print(f"[bold red]❌ Database not found:[/bold red] {db}")
        console.print(
            "💡 Run [cyan]llamaball ingest[/cyan] first to create the database"
        )
        raise typer.Exit(1)

    # Show chat configuration
    if debug:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)
        console.print("[bold]Chat Configuration:[/bold]")
        console.print(f"🗄️  Database: [cyan]{db}[/cyan]")
        console.print(f"🔍 Embedding Model: [cyan]{model}[/cyan]")
        console.print(f"💬 Chat Model: [cyan]{chat_model}[/cyan]")
        console.print(f"📊 Top-K: [cyan]{topk}[/cyan]")
        console.print(f"🌡️  Temperature: [cyan]{temperature}[/cyan]")
        console.print()

    # Get database stats
    stats_info = get_db_stats(db)

    # Welcome message
    welcome_panel = Panel(
        f"""[bold green]🦙 Llamaball Chat Session[/bold green]
        
📊 Database: {stats_info['docs']} documents, {stats_info['embeddings']} embeddings
🤖 Chat Model: [cyan]{chat_model}[/cyan]
🔍 Retrieval: Top {topk} relevant documents

[dim]Commands: 'exit', 'quit', 'help', 'stats', 'clear'[/dim]
[dim]Press Ctrl+C or type 'exit' to end session[/dim]""",
        title="Chat Ready",
        border_style="green",
    )
    console.print(welcome_panel)

    # Start interactive chat
    start_interactive_chat(
        db,
        model,
        provider,
        chat_model,
        topk,
        system_prompt,
        debug,
        temperature,
        max_tokens,
        top_p,
        top_k,
        repeat_penalty,
    )


@app.command(name="stats")
def stats_command(
    db: str = typer.Option(
        core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed statistics"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, plain"
    ),
):
    """
    📊 Show database statistics and information.

    Display comprehensive information about your document database including
    document counts, file types, recent activity, and storage usage.

    Examples:
      llamaball stats                    # Basic statistics
      llamaball stats -v                 # Detailed statistics
      llamaball stats --format json      # JSON output
    """
    if not Path(db).exists():
        console.print(f"[bold red]❌ Database not found:[/bold red] {db}")
        raise typer.Exit(1)

    stats_info = get_detailed_stats(db, verbose)

    if format == "json":
        import json

        console.print(json.dumps(stats_info, indent=2))
    elif format == "plain":
        console.print(f"Documents: {stats_info['docs']}")
        console.print(f"Embeddings: {stats_info['embeddings']}")
        console.print(f"Files: {stats_info['files']}")
    else:
        display_stats_table(stats_info, verbose)


@app.command(name="list")
def list_files_command(
    db: str = typer.Option(
        core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"
    ),
    filter: str = typer.Option("", "--filter", "-f", help="Filter files by pattern"),
    sort: str = typer.Option("name", "--sort", "-s", help="Sort by: name, date, size"),
    limit: int = typer.Option(
        0, "--limit", "-l", help="Limit number of results (0 = no limit)"
    ),
):
    """
    📋 List all files in the database.

    Show all ingested files with metadata including modification times,
    file sizes, and document counts.

    Examples:
      llamaball list                     # List all files
      llamaball list --filter "*.py"     # List Python files only
      llamaball list --sort date         # Sort by modification date
      llamaball list --limit 10          # Show only first 10 files
    """
    if not Path(db).exists():
        console.print(f"[bold red]❌ Database not found:[/bold red] {db}")
        raise typer.Exit(1)

    files_info = get_files_list(db, filter, sort, limit)
    display_files_table(files_info)


@app.command(name="clear")
def clear_db_command(
    db: str = typer.Option(
        core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    backup: bool = typer.Option(
        True, "--backup/--no-backup", "-b", help="Create backup before clearing"
    ),
):
    """
    🗑️  Clear the database (delete all data).

    This command will remove all documents, embeddings, and file records from
    the database. Use with caution as this action cannot be undone.

    Examples:
      llamaball clear                    # Clear with confirmation
      llamaball clear --force            # Clear without confirmation
      llamaball clear --no-backup        # Clear without backup
    """
    if not Path(db).exists():
        console.print(f"[bold yellow]⚠️  Database not found:[/bold yellow] {db}")
        console.print("Nothing to clear.")
        return

    # Show current stats
    stats_info = get_db_stats(db)

    if not force:
        console.print(f"\n[bold red]⚠️  WARNING:[/bold red] This will delete:")
        console.print(f"📄 {stats_info['docs']} documents")
        console.print(f"🔢 {stats_info['embeddings']} embeddings")
        console.print(f"📁 {stats_info['files']} file records")
        console.print()

        if not typer.confirm(
            "Are you sure you want to clear the database?", default=False
        ):
            console.print("❌ Operation cancelled")
            return

    # Create backup if requested
    if backup:
        import datetime
        import shutil

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db}.backup_{timestamp}"
        shutil.copy2(db, backup_path)
        console.print(f"💾 Backup created: [cyan]{backup_path}[/cyan]")

    # Clear the database
    try:
        core.init_db(db)
        console.print("[bold green]✅ Database cleared successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ Failed to clear database:[/bold red] {e}")
        raise typer.Exit(1)


@app.command(name="models")
def models_command(
    custom_model: Optional[str] = typer.Argument(
        None, help="Show details for a specific model"
    ),
    format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, plain"
    ),
):
    """
    🤖 List available Ollama models.

    Display all locally available models with their sizes, families, and parameters.
    Useful for choosing which model to use for chat sessions.

    Examples:
      llamaball models                        # List all models
      llamaball models llamaball-qwen3:4b     # Show specific model details
      llamaball models --format json         # JSON output
    """
    from .core import format_model_size, get_available_models

    models = get_available_models(custom_model)

    if not models:
        console.print("[yellow]No models found. Make sure Ollama is running.[/yellow]")
        return

    if format == "json":
        import json

        console.print(json.dumps(models, indent=2))
    elif format == "plain":
        for model in models:
            console.print(f"{model['name']}")
    else:
        if custom_model and len(models) == 1:
            # Show detailed info for single model
            model = models[0]
            details = model.get("details", {})
            console.print(f"[bold]Model:[/bold] {model['name']}")
            console.print(f"[bold]Size:[/bold] {format_model_size(model['size'])}")
            console.print(f"[bold]Family:[/bold] {details.get('family', 'unknown')}")
            console.print(
                f"[bold]Parameters:[/bold] {details.get('parameter_size', 'unknown')}"
            )
            console.print(
                f"[bold]Quantization:[/bold] {details.get('quantization_level', 'unknown')}"
            )
        else:
            list_available_models(custom_model)


@app.command(name="version")
def version_command():
    """Show version information."""
    from . import __version__
    console.print(f"[bold]Llamaball[/bold] version [green]{__version__}[/green]")
    console.print("🦙 High-performance document chat and RAG system")
    console.print("Built with ❤️  for local AI and accessibility")


# Helper functions


def get_db_stats(db_path: str) -> dict:
    """Get basic database statistics"""
    import sqlite3

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        docs = c.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        embeddings = c.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
        files = c.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        conn.close()
        return {"docs": docs, "embeddings": embeddings, "files": files}
    except Exception:
        return {"docs": 0, "embeddings": 0, "files": 0}


def get_detailed_stats(db_path: str, verbose: bool = False) -> dict:
    """Get detailed database statistics"""
    import os
    import sqlite3

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Basic counts
    docs = c.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    embeddings = c.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
    files = c.execute("SELECT COUNT(*) FROM files").fetchone()[0]

    # Database size
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

    stats = {
        "docs": docs,
        "embeddings": embeddings,
        "files": files,
        "db_size_mb": round(db_size / 1024 / 1024, 2),
    }

    if verbose:
        # File type breakdown
        file_types = c.execute(
            """
            SELECT SUBSTR(filename, INSTR(filename, '.') + 1) as ext, COUNT(*) 
            FROM files 
            WHERE INSTR(filename, '.') > 0 
            GROUP BY ext 
            ORDER BY COUNT(*) DESC
        """
        ).fetchall()
        stats["file_types"] = dict(file_types)

        # Recent activity
        recent_files = c.execute(
            """
            SELECT filename, mtime 
            FROM files 
            ORDER BY mtime DESC 
            LIMIT 5
        """
        ).fetchall()
        stats["recent_files"] = recent_files

    conn.close()
    return stats


def get_files_list(
    db_path: str, filter_pattern: str = "", sort_by: str = "name", limit: int = 0
) -> list:
    """Get list of files with optional filtering and sorting"""
    import sqlite3

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    query = "SELECT filename, mtime FROM files"
    params = []

    if filter_pattern:
        query += " WHERE filename LIKE ?"
        params.append(f"%{filter_pattern}%")

    if sort_by == "date":
        query += " ORDER BY mtime DESC"
    elif sort_by == "size":
        query += " ORDER BY LENGTH(filename) DESC"
    else:
        query += " ORDER BY filename"

    if limit > 0:
        query += " LIMIT ?"
        params.append(limit)

    files = c.execute(query, params).fetchall()
    conn.close()
    return files


def display_stats_table(stats_info: dict, verbose: bool = False):
    """Display statistics in a formatted table"""
    table = Table(
        title="📊 Database Statistics", show_header=True, header_style="bold magenta"
    )
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("📄 Documents", str(stats_info["docs"]))
    table.add_row("🔢 Embeddings", str(stats_info["embeddings"]))
    table.add_row("📁 Files", str(stats_info["files"]))
    table.add_row("💾 Database Size", f"{stats_info['db_size_mb']} MB")

    if verbose and "file_types" in stats_info:
        for ext, count in list(stats_info["file_types"].items())[:5]:
            table.add_row(f"📝 .{ext} files", str(count))

    console.print(table)


def display_files_table(files_info: list):
    """Display files in a formatted table"""
    if not files_info:
        console.print("[yellow]No files found in database[/yellow]")
        return

    table = Table(
        title="📋 Ingested Files", show_header=True, header_style="bold magenta"
    )
    table.add_column("Filename", style="cyan")
    table.add_column("Modified", style="green")

    for filename, mtime in files_info:
        import datetime

        mod_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(filename, mod_time)

    console.print(table)


def start_interactive_chat(
    db: str,
    model: str,
    provider: str,
    chat_model: str,
    topk: int,
    system_prompt: Optional[str] = None,
    debug: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 512,
    top_p: float = 0.9,
    top_k: int = 40,
    repeat_penalty: float = 1.1,
):
    """Start the interactive chat session"""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.shortcuts import print_formatted_text
    from prompt_toolkit.styles import Style

    CLI_STYLE = Style.from_dict(
        {
            "b": "bold ansigreen",
            "ans": "ansicyan",
            "i": "italic",
            "u": "underline ansiyellow",
        }
    )

    prompt_session = PromptSession(style=CLI_STYLE)
    chat_session = ChatSession(db, model, provider, chat_model, topk, system_prompt)

    # Set initial parameters from CLI
    chat_session.temperature = temperature
    chat_session.max_tokens = max_tokens
    chat_session.top_p = top_p
    chat_session.top_k = top_k
    chat_session.repeat_penalty = repeat_penalty

    while True:
        try:
            user_input = prompt_session.prompt(HTML("<b>🤔 You:</b> "), style=CLI_STYLE)

            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]👋 Goodbye![/dim]")
                break
            elif user_input.lower() == "help":
                show_chat_help()
                continue
            elif user_input.lower() == "stats":
                stats_info = get_db_stats(db)
                console.print(
                    f"📊 {stats_info['docs']} docs, {stats_info['embeddings']} embeddings"
                )
                continue
            elif user_input.lower() == "clear":
                chat_session.reset_history()
                console.print("[dim]🧹 Conversation history cleared[/dim]")
                continue
            elif not user_input.strip():
                continue

            # Check for chat commands (model switching, parameter changes, etc.)
            command_result = handle_chat_command(user_input, chat_session)
            if command_result is not None:
                # It was a command, display the result
                console.print(f"[cyan]🔧 System:[/cyan]\n{command_result}\n")
                continue

            # Show thinking indicator
            with console.status("🤖 Thinking...") as status:
                try:
                    response = core.chat(
                        db=chat_session.db,
                        model=chat_session.model,
                        provider=chat_session.provider,
                        chat_model=chat_session.chat_model,
                        topk=chat_session.topk,
                        user_input=user_input,
                        history=chat_session.history.copy(),
                        temperature=chat_session.temperature,
                        max_tokens=chat_session.max_tokens,
                        top_p=chat_session.top_p,
                        top_k=chat_session.top_k,
                        repeat_penalty=chat_session.repeat_penalty,
                    )
                    chat_session.history.append({"role": "user", "content": user_input})
                    chat_session.history.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    console.print(f"[bold red]❌ Error:[/bold red] {e}")
                    if debug:
                        import traceback

                        console.print("[dim]" + traceback.format_exc() + "[/dim]")
                    continue

            # Display response
            print_formatted_text(
                HTML(f"<ans>🦙 Assistant:</ans>\n{response}\n"), style=CLI_STYLE
            )

        except KeyboardInterrupt:
            console.print("\n[dim]👋 Goodbye![/dim]")
            break
        except EOFError:
            console.print("\n[dim]👋 Goodbye![/dim]")
            break


def show_chat_help():
    """Show help during chat session"""
    help_text = """
[bold]💬 Chat Session Help[/bold]

[bold]Basic Commands:[/bold]
• [cyan]exit, quit, q[/cyan] - End the chat session
• [cyan]help[/cyan] - Show this help message
• [cyan]stats[/cyan] - Show database statistics
• [cyan]clear[/cyan] - Clear conversation history

[bold]Model & Parameter Commands:[/bold]
• [cyan]/models[/cyan] - List available models
• [cyan]/model [name][/cyan] - Switch to a different model
• [cyan]/temp [0.0-2.0][/cyan] - Change response creativity
• [cyan]/tokens [1-8192][/cyan] - Change max response length
• [cyan]/topk [1-20][/cyan] - Change document retrieval count
• [cyan]/status[/cyan] - Show current settings
• [cyan]/commands[/cyan] - Show all available commands

[bold]Tips:[/bold]
• Ask specific questions about your documents
• Use natural language - no special syntax needed
• Reference specific files or topics for better results
• The assistant can execute code and run commands if needed
• Change models on-the-fly with [cyan]/model[/cyan] command
• Adjust creativity with [cyan]/temp[/cyan] (0.0=focused, 1.0=creative)

[bold]Shortcuts:[/bold]
• [cyan]Ctrl+C[/cyan] - End session
• [cyan]Ctrl+D[/cyan] - End session (Unix/Mac)
"""
    console.print(Panel(help_text, title="Chat Help", border_style="blue"))


class ChatSession:
    """Manages chat session state including model selection and parameters"""

    def __init__(self, db, model, provider, chat_model, topk, system_prompt=None):
        self.db = db
        self.model = model
        self.provider = provider
        self.chat_model = chat_model
        self.topk = topk
        self.system_prompt = system_prompt
        self.history = []
        self.temperature = 0.7
        self.max_tokens = 512
        self.top_p = 0.9
        self.top_k = 40
        self.repeat_penalty = 1.1

        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    def reset_history(self):
        """Reset conversation history"""
        self.history = []
        if self.system_prompt:
            self.history.append({"role": "system", "content": self.system_prompt})

    def get_status(self):
        """Get current session configuration as a formatted string"""
        return f"""🤖 Current Settings:
• Model: {self.chat_model}
• Temperature: {self.temperature}
• Max Tokens: {self.max_tokens}
• Top-K Retrieval: {self.topk}
• Top-P: {self.top_p}
• Top-K Sampling: {self.top_k}
• Repeat Penalty: {self.repeat_penalty}"""


def list_available_models(custom_model=None):
    """List available models with size information"""
    from rich.table import Table

    from .core import format_model_size, get_available_models

    models = get_available_models(custom_model)

    if not models:
        console.print("[yellow]No models found[/yellow]")
        return

    table = Table(
        title="🤖 Available Models", show_header=True, header_style="bold magenta"
    )
    table.add_column("Model Name", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Family", style="blue")
    table.add_column("Parameters", style="yellow")

    for model in models:
        details = model.get("details", {})
        family = details.get("family", "unknown")
        param_size = details.get("parameter_size", "unknown")
        size_str = format_model_size(model["size"])

        table.add_row(model["name"], size_str, family, param_size)

    console.print(table)
    return models


def handle_chat_command(user_input: str, session: ChatSession) -> str:
    """
    Handle special chat commands for changing settings.
    Returns None if it's a regular chat message, or a response string for commands.
    """
    user_input = user_input.strip()

    if user_input.startswith("/"):
        parts = user_input[1:].split()
        command = parts[0].lower() if parts else ""

        if command == "models":
            # List available models
            custom_model = parts[1] if len(parts) > 1 else None
            list_available_models(custom_model)
            return "Listed available models above"

        elif command == "model" and len(parts) > 1:
            # Change model: /model llamaball-qwen3:0.6b
            new_model = parts[1]
            session.chat_model = new_model
            return f"✅ Changed chat model to: {new_model}"

        elif command == "temp" and len(parts) > 1:
            # Change temperature: /temp 0.8
            try:
                new_temp = float(parts[1])
                if 0.0 <= new_temp <= 2.0:
                    session.temperature = new_temp
                    return f"✅ Changed temperature to: {new_temp}"
                else:
                    return "❌ Temperature must be between 0.0 and 2.0"
            except ValueError:
                return "❌ Invalid temperature value. Use a number between 0.0 and 2.0"

        elif command == "tokens" and len(parts) > 1:
            # Change max tokens: /tokens 1024
            try:
                new_tokens = int(parts[1])
                if 1 <= new_tokens <= 8192:
                    session.max_tokens = new_tokens
                    return f"✅ Changed max tokens to: {new_tokens}"
                else:
                    return "❌ Max tokens must be between 1 and 8192"
            except ValueError:
                return "❌ Invalid token value. Use a whole number between 1 and 8192"

        elif command == "topk" and len(parts) > 1:
            # Change top-k retrieval: /topk 5
            try:
                new_topk = int(parts[1])
                if 1 <= new_topk <= 20:
                    session.topk = new_topk
                    return f"✅ Changed top-K retrieval to: {new_topk}"
                else:
                    return "❌ Top-K must be between 1 and 20"
            except ValueError:
                return "❌ Invalid top-K value. Use a whole number between 1 and 20"

        elif command == "topp" and len(parts) > 1:
            # Change top-p: /topp 0.9
            try:
                new_topp = float(parts[1])
                if 0.0 <= new_topp <= 1.0:
                    session.top_p = new_topp
                    return f"✅ Changed top-P to: {new_topp}"
                else:
                    return "❌ Top-P must be between 0.0 and 1.0"
            except ValueError:
                return "❌ Invalid top-P value. Use a number between 0.0 and 1.0"

        elif command == "penalty" and len(parts) > 1:
            # Change repeat penalty: /penalty 1.1
            try:
                new_penalty = float(parts[1])
                if 0.0 <= new_penalty <= 2.0:
                    session.repeat_penalty = new_penalty
                    return f"✅ Changed repeat penalty to: {new_penalty}"
                else:
                    return "❌ Repeat penalty must be between 0.0 and 2.0"
            except ValueError:
                return (
                    "❌ Invalid repeat penalty value. Use a number between 0.0 and 2.0"
                )

        elif command == "status":
            # Show current settings
            return session.get_status()

        elif command == "commands":
            # Show available commands
            return """🔧 Available Commands:
• /models [custom_model] - List available models
• /model [name] - Change chat model
• /temp [0.0-2.0] - Change temperature
• /tokens [1-8192] - Change max tokens
• /topk [1-20] - Change document retrieval count
• /topp [0.0-1.0] - Change top-P sampling
• /penalty [0.0-2.0] - Change repeat penalty
• /status - Show current settings
• /commands - Show this help
• help, stats, clear, exit, quit - Standard commands"""

        else:
            return f"❌ Unknown command: /{command}. Type '/commands' for help."

    # Not a command, return None to indicate regular chat
    return None


def main():
    """Main entry point"""
    # If no arguments provided, show welcome and help
    if len(sys.argv) == 1:
        show_welcome()
        return

    app()


if __name__ == "__main__":
    main()
