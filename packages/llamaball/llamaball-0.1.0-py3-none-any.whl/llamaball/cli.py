#!/usr/bin/env python3
"""
Llamaball CLI - Accessible document chat and RAG system
File Purpose: Interactive command-line interface for llamaball
Primary Functions: ingest, chat, stats, list-files, clear-db
Inputs: CLI arguments and interactive prompts
Outputs: Formatted terminal output with accessibility features
"""

import typer
import sys
from typing import Optional
from pathlib import Path
from llamaball import core
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

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
  llamaball ingest .                    # Ingest current directory
  llamaball ingest ~/docs -r            # Recursively ingest docs folder
  llamaball chat                        # Start interactive chat
  llamaball chat --model qwen3:0.6b     # Chat with specific model
  llamaball stats                       # Show database statistics
  
Get started:
  1. llamaball ingest --dir /path/to/docs
  2. llamaball chat
  3. Ask questions about your documents!
""",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False
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
    version: bool = typer.Option(False, "--version", "-v", help="Show version information"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Enable verbose logging")
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
    directory: Optional[str] = typer.Argument(None, help="Directory to ingest (default: current directory)"),
    db: str = typer.Option(core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"),
    model: str = typer.Option(core.DEFAULT_MODEL_NAME, "--model", "-m", help="Embedding model name"),
    provider: str = typer.Option(core.DEFAULT_PROVIDER, "--provider", "-p", help="Provider: ollama or openai"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Recursively ingest subdirectories"),
    exclude: str = typer.Option("", "--exclude", "-e", help="Exclude patterns (comma-separated)"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-indexing of all files"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output")
):
    """
    📚 Ingest documents and build embeddings database.
    
    This command scans the specified directory, extracts text from supported files,
    chunks the content intelligently, and creates embeddings for semantic search.
    
    Supported file types: .txt, .md, .py, .json, .csv
    
    Examples:
      llamaball ingest                    # Ingest current directory
      llamaball ingest ./docs -r          # Recursively ingest docs/
      llamaball ingest ~/papers -m qwen3  # Use different model
      llamaball ingest . --exclude "*.log,temp*"  # Exclude patterns
    """
    # Use current directory if none specified
    if directory is None:
        directory = "."
    
    # Validate directory exists
    dir_path = Path(directory)
    if not dir_path.exists():
        console.print(f"[bold red]Error:[/bold red] Directory '{directory}' does not exist")
        raise typer.Exit(1)
    
    if not dir_path.is_dir():
        console.print(f"[bold red]Error:[/bold red] '{directory}' is not a directory")
        raise typer.Exit(1)
    
    # Interactive confirmation for recursive mode
    if not recursive and not quiet:
        recursive = typer.confirm(
            f"📁 Recursively scan subdirectories in '{directory}'?",
            default=False
        )
    
    # Parse exclude patterns
    exclude_patterns = [p.strip() for p in exclude.split(',') if p.strip()] if exclude else []
    
    # Show what we're about to do
    if not quiet:
        console.print(f"\n[bold]Ingestion Configuration:[/bold]")
        console.print(f"📂 Directory: [cyan]{directory}[/cyan]")
        console.print(f"🗄️  Database: [cyan]{db}[/cyan]")
        console.print(f"🤖 Model: [cyan]{model}[/cyan]")
        console.print(f"🔄 Recursive: [cyan]{recursive}[/cyan]")
        console.print(f"🚫 Exclude: [cyan]{exclude if exclude else 'none'}[/cyan]")
        console.print()
    
    try:
        if not quiet:
            with console.status("🔍 Processing documents..."):
                core.ingest_files(directory, db, model, provider, recursive, exclude_patterns)
        else:
            core.ingest_files(directory, db, model, provider, recursive, exclude_patterns)
        
        if not quiet:
            console.print("[bold green]✅ Ingestion completed successfully![/bold green]")
            # Show quick stats
            stats_info = get_db_stats(db)
            console.print(f"📊 Indexed {stats_info['docs']} documents with {stats_info['embeddings']} embeddings")
            
    except Exception as e:
        console.print(f"[bold red]❌ Ingestion failed:[/bold red] {e}")
        if not quiet:  # Show traceback in non-quiet mode instead of verbose
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)

@app.command(name="chat")
def chat_command(
    db: str = typer.Option(core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"),
    model: str = typer.Option(core.DEFAULT_MODEL_NAME, "--model", "-m", help="Embedding model"),
    provider: str = typer.Option(core.DEFAULT_PROVIDER, "--provider", "-p", help="Provider: ollama or openai"),
    chat_model: str = typer.Option(core.DEFAULT_CHAT_MODEL, "--chat-model", "-c", help="Chat model name"),
    topk: int = typer.Option(3, "--top-k", "-k", help="Number of relevant documents to retrieve"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Chat model temperature (0.0-2.0)"),
    max_tokens: int = typer.Option(512, "--max-tokens", "-T", help="Maximum tokens in response"),
    system_prompt: Optional[str] = typer.Option(None, "--system", "-s", help="Custom system prompt"),
    debug: bool = typer.Option(False, "--debug", help="Show debug information")
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
      llamaball chat                           # Basic chat
      llamaball chat -c qwen3:4b               # Use specific chat model
      llamaball chat --top-k 5 --temp 0.3     # More documents, lower temperature
      llamaball chat --system "Be concise"    # Custom system prompt
    """
    # Check if database exists
    db_path = Path(db)
    if not db_path.exists():
        console.print(f"[bold red]❌ Database not found:[/bold red] {db}")
        console.print("💡 Run [cyan]llamaball ingest[/cyan] first to create the database")
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
        border_style="green"
    )
    console.print(welcome_panel)
    
    # Start interactive chat
    start_interactive_chat(db, model, provider, chat_model, topk, system_prompt, debug)

@app.command(name="stats")
def stats_command(
    db: str = typer.Option(core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed statistics"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, plain")
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
    db: str = typer.Option(core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"),
    filter: str = typer.Option("", "--filter", "-f", help="Filter files by pattern"),
    sort: str = typer.Option("name", "--sort", "-s", help="Sort by: name, date, size"),
    limit: int = typer.Option(0, "--limit", "-l", help="Limit number of results (0 = no limit)")
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
    db: str = typer.Option(core.DEFAULT_DB_PATH, "--database", "-d", help="SQLite database path"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    backup: bool = typer.Option(True, "--backup/--no-backup", "-b", help="Create backup before clearing")
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
        
        if not typer.confirm("Are you sure you want to clear the database?", default=False):
            console.print("❌ Operation cancelled")
            return
    
    # Create backup if requested
    if backup:
        import shutil
        import datetime
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

@app.command(name="version")
def version_command():
    """Show version information."""
    console.print("[bold]Llamaball[/bold] version [green]0.1.0[/green]")
    console.print("🦙 Accessible document chat and RAG system")
    console.print("Built with ❤️  for accessibility and local AI")

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
    import sqlite3
    import os
    
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
        "db_size_mb": round(db_size / 1024 / 1024, 2)
    }
    
    if verbose:
        # File type breakdown
        file_types = c.execute("""
            SELECT SUBSTR(filename, INSTR(filename, '.') + 1) as ext, COUNT(*) 
            FROM files 
            WHERE INSTR(filename, '.') > 0 
            GROUP BY ext 
            ORDER BY COUNT(*) DESC
        """).fetchall()
        stats["file_types"] = dict(file_types)
        
        # Recent activity
        recent_files = c.execute("""
            SELECT filename, mtime 
            FROM files 
            ORDER BY mtime DESC 
            LIMIT 5
        """).fetchall()
        stats["recent_files"] = recent_files
    
    conn.close()
    return stats

def get_files_list(db_path: str, filter_pattern: str = "", sort_by: str = "name", limit: int = 0) -> list:
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
    table = Table(title="📊 Database Statistics", show_header=True, header_style="bold magenta")
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
    
    table = Table(title="📋 Ingested Files", show_header=True, header_style="bold magenta")
    table.add_column("Filename", style="cyan")
    table.add_column("Modified", style="green")
    
    for filename, mtime in files_info:
        import datetime
        mod_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(filename, mod_time)
    
    console.print(table)

def start_interactive_chat(db: str, model: str, provider: str, chat_model: str, topk: int, 
                          system_prompt: Optional[str] = None, debug: bool = False):
    """Start the interactive chat session"""
    from prompt_toolkit import PromptSession
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.styles import Style
    from prompt_toolkit.shortcuts import print_formatted_text
    
    CLI_STYLE = Style.from_dict({
        "b": "bold ansigreen",
        "ans": "ansicyan", 
        "i": "italic",
        "u": "underline ansiyellow"
    })
    
    session = PromptSession(style=CLI_STYLE)
    history = []
    
    if system_prompt:
        history.append({"role": "system", "content": system_prompt})
    
    while True:
        try:
            user_input = session.prompt(HTML("<b>🤔 You:</b> "), style=CLI_STYLE)
            
            if user_input.lower() in ("exit", "quit", "q"):
                console.print("[dim]👋 Goodbye![/dim]")
                break
            elif user_input.lower() == "help":
                show_chat_help()
                continue
            elif user_input.lower() == "stats":
                stats_info = get_db_stats(db)
                console.print(f"📊 {stats_info['docs']} docs, {stats_info['embeddings']} embeddings")
                continue
            elif user_input.lower() == "clear":
                history = []
                if system_prompt:
                    history.append({"role": "system", "content": system_prompt})
                console.print("[dim]🧹 Conversation history cleared[/dim]")
                continue
            elif not user_input.strip():
                continue
            
            # Show thinking indicator
            with console.status("🤖 Thinking...") as status:
                try:
                    response = core.chat(db, model, provider, chat_model, topk, user_input, history.copy())
                    history.append({"role": "user", "content": user_input})
                    history.append({"role": "assistant", "content": response})
                except Exception as e:
                    console.print(f"[bold red]❌ Error:[/bold red] {e}")
                    if debug:
                        import traceback
                        console.print("[dim]" + traceback.format_exc() + "[/dim]")
                    continue
            
            # Display response
            print_formatted_text(HTML(f"<ans>🦙 Assistant:</ans>\n{response}\n"), style=CLI_STYLE)
            
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

[bold]Commands:[/bold]
• [cyan]exit, quit, q[/cyan] - End the chat session
• [cyan]help[/cyan] - Show this help message
• [cyan]stats[/cyan] - Show database statistics
• [cyan]clear[/cyan] - Clear conversation history

[bold]Tips:[/bold]
• Ask specific questions about your documents
• Use natural language - no special syntax needed
• Reference specific files or topics for better results
• The assistant can execute code and run commands if needed

[bold]Shortcuts:[/bold]
• [cyan]Ctrl+C[/cyan] - End session
• [cyan]Ctrl+D[/cyan] - End session (Unix/Mac)
"""
    console.print(Panel(help_text, title="Chat Help", border_style="blue"))

def main():
    """Main entry point"""
    # If no arguments provided, show welcome and help
    if len(sys.argv) == 1:
        show_welcome()
        return
    
    app()

if __name__ == "__main__":
    main() 