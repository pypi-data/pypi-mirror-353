#!/usr/bin/env python3
"""
Llamaball Web Server
File Purpose: Flask-based web interface for Llamaball RAG system
Primary Functions: Web UI, API endpoints, file upload, chat interface
Inputs: HTTP requests, file uploads, chat messages
Outputs: HTML pages, JSON API responses, real-time chat
"""

import os
import json
import logging
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.serving import WSGIRequestHandler

from . import core
from .parsers import get_supported_extensions, is_supported_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'llamaball-dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Enable CORS for API endpoints
CORS(app, origins=['*'])

# Global configuration
DEFAULT_DB_PATH = os.environ.get('LLAMABALL_DB_PATH', '.llamaball.db')
DEFAULT_MODEL = os.environ.get('LLAMABALL_MODEL', 'nomic-embed-text:latest')
DEFAULT_CHAT_MODEL = os.environ.get('LLAMABALL_CHAT_MODEL', 'llama3.2:1b')
UPLOAD_FOLDER = os.environ.get('LLAMABALL_UPLOAD_FOLDER', './uploads')
ALLOWED_EXTENSIONS = get_supported_extensions()

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global chat sessions storage
chat_sessions = {}

class WSGIRequestHandler(WSGIRequestHandler):
    """Custom request handler to suppress logs in production"""
    def log_request(self, code='-', size='-'):
        if app.debug:
            super().log_request(code, size)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get database statistics
        stats = get_database_stats()
        
        # Get recent files
        recent_files = get_recent_files(limit=10)
        
        # Get available models
        models = core.get_available_models()
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_files=recent_files,
                             models=models,
                             supported_extensions=list(ALLOWED_EXTENSIONS))
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/chat')
def chat_page():
    """Interactive chat interface"""
    try:
        # Initialize session if needed
        if 'session_id' not in session:
            session['session_id'] = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_id = session['session_id']
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'history': [],
                'created': datetime.now(),
                'model': DEFAULT_CHAT_MODEL
            }
        
        # Get database stats for context
        stats = get_database_stats()
        
        return render_template('chat.html', 
                             session_id=session_id,
                             stats=stats,
                             default_model=DEFAULT_CHAT_MODEL)
    except Exception as e:
        logger.error(f"Error loading chat page: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/upload')
def upload_page():
    """File upload interface"""
    return render_template('upload.html', 
                         supported_extensions=list(ALLOWED_EXTENSIONS),
                         max_file_size_mb=app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))

@app.route('/stats')
def stats_page():
    """Detailed statistics page"""
    try:
        stats = get_detailed_stats()
        return render_template('stats.html', stats=stats)
    except Exception as e:
        logger.error(f"Error loading stats page: {e}")
        return render_template('error.html', error=str(e)), 500

# API Endpoints

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        session_id = data.get('session_id', 'default')
        model = data.get('model', DEFAULT_CHAT_MODEL)
        top_k = data.get('top_k', 3)
        temperature = data.get('temperature', 0.7)
        
        # Get or create session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'history': [],
                'created': datetime.now(),
                'model': model
            }
        
        chat_session = chat_sessions[session_id]
        
        # Generate response
        response = core.chat(
            db=DEFAULT_DB_PATH,
            model=DEFAULT_MODEL,
            provider='ollama',
            chat_model=model,
            topk=top_k,
            user_input=user_message,
            history=chat_session['history'].copy(),
            temperature=temperature
        )
        
        # Update session history
        chat_session['history'].append({'role': 'user', 'content': user_message})
        chat_session['history'].append({'role': 'assistant', 'content': response})
        
        # Keep history manageable (last 20 messages)
        if len(chat_session['history']) > 20:
            chat_session['history'] = chat_session['history'][-20:]
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search API endpoint"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 5)
        
        results = core.search_embeddings(
            query=query,
            db_path=DEFAULT_DB_PATH,
            model_name=DEFAULT_MODEL,
            top_k=top_k,
            provider='ollama'
        )
        
        # Format results for JSON response
        formatted_results = []
        for filename, content, score in results:
            formatted_results.append({
                'filename': filename,
                'content': content[:500] + '...' if len(content) > 500 else content,
                'score': float(score),
                'preview': content[:200] + '...' if len(content) > 200 else content
            })
        
        return jsonify({
            'results': formatted_results,
            'query': query,
            'total_results': len(formatted_results)
        })
        
    except Exception as e:
        logger.error(f"Search API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """File upload API endpoint"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid conflicts
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    try:
                        file.save(filepath)
                        uploaded_files.append({
                            'filename': filename,
                            'original_name': file.filename,
                            'size': os.path.getsize(filepath),
                            'path': filepath
                        })
                    except Exception as e:
                        errors.append(f"Failed to save {file.filename}: {str(e)}")
                else:
                    errors.append(f"File type not supported: {file.filename}")
        
        # Trigger ingestion in background
        if uploaded_files:
            threading.Thread(
                target=ingest_uploaded_files,
                args=(uploaded_files,),
                daemon=True
            ).start()
        
        return jsonify({
            'uploaded_files': uploaded_files,
            'errors': errors,
            'message': f'Successfully uploaded {len(uploaded_files)} files. Ingestion started in background.'
        })
        
    except Exception as e:
        logger.error(f"Upload API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ingest', methods=['POST'])
def api_ingest():
    """Manual ingestion trigger API endpoint"""
    try:
        data = request.get_json() or {}
        directory = data.get('directory', UPLOAD_FOLDER)
        recursive = data.get('recursive', True)
        force = data.get('force', False)
        
        # Run ingestion in background
        threading.Thread(
            target=run_ingestion,
            args=(directory, recursive, force),
            daemon=True
        ).start()
        
        return jsonify({
            'message': 'Ingestion started in background',
            'directory': directory,
            'recursive': recursive,
            'force': force
        })
        
    except Exception as e:
        logger.error(f"Ingest API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """Statistics API endpoint"""
    try:
        stats = get_detailed_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models')
def api_models():
    """Available models API endpoint"""
    try:
        models = core.get_available_models()
        return jsonify({'models': models})
    except Exception as e:
        logger.error(f"Models API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    try:
        # Check database
        stats = get_database_stats()
        
        # Check Ollama connection
        models = core.get_available_models()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ollama': 'connected' if models else 'disconnected',
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Helper functions

def get_database_stats():
    """Get basic database statistics"""
    try:
        import sqlite3
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        c = conn.cursor()
        
        docs = c.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        embeddings = c.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
        files = c.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        
        conn.close()
        
        return {
            'documents': docs,
            'embeddings': embeddings,
            'files': files,
            'database_size': get_file_size(DEFAULT_DB_PATH)
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            'documents': 0,
            'embeddings': 0,
            'files': 0,
            'database_size': 0
        }

def get_detailed_stats():
    """Get detailed database statistics"""
    try:
        import sqlite3
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        c = conn.cursor()
        
        # Basic stats
        basic_stats = get_database_stats()
        
        # File types
        file_types = c.execute("""
            SELECT SUBSTR(filename, INSTR(filename, '.') + 1) as ext, COUNT(*) 
            FROM files 
            WHERE INSTR(filename, '.') > 0 
            GROUP BY ext 
            ORDER BY COUNT(*) DESC
        """).fetchall()
        
        # Recent files
        recent_files = c.execute("""
            SELECT filename, mtime 
            FROM files 
            ORDER BY mtime DESC 
            LIMIT 10
        """).fetchall()
        
        conn.close()
        
        return {
            **basic_stats,
            'file_types': dict(file_types),
            'recent_files': [{'filename': f[0], 'mtime': f[1]} for f in recent_files]
        }
    except Exception as e:
        logger.error(f"Error getting detailed stats: {e}")
        return get_database_stats()

def get_recent_files(limit=10):
    """Get recently added files"""
    try:
        import sqlite3
        conn = sqlite3.connect(DEFAULT_DB_PATH)
        c = conn.cursor()
        
        files = c.execute("""
            SELECT filename, mtime 
            FROM files 
            ORDER BY mtime DESC 
            LIMIT ?
        """, (limit,)).fetchall()
        
        conn.close()
        
        return [{'filename': f[0], 'mtime': f[1]} for f in files]
    except Exception:
        return []

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath) if os.path.exists(filepath) else 0
    except Exception:
        return 0

def ingest_uploaded_files(uploaded_files):
    """Background task to ingest uploaded files"""
    try:
        logger.info(f"Starting ingestion of {len(uploaded_files)} uploaded files")
        
        # Create temporary directory with uploaded files
        temp_dir = tempfile.mkdtemp()
        
        for file_info in uploaded_files:
            # Move file to temp directory for ingestion
            src_path = file_info['path']
            dst_path = os.path.join(temp_dir, file_info['original_name'])
            os.rename(src_path, dst_path)
        
        # Run ingestion
        stats = core.ingest_files(
            directory=temp_dir,
            db_path=DEFAULT_DB_PATH,
            model_name=DEFAULT_MODEL,
            provider='ollama',
            recursive=False,
            exclude_patterns=[],
            force=False
        )
        
        logger.info(f"Ingestion completed: {stats}")
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        logger.error(f"Error in background ingestion: {e}")

def run_ingestion(directory, recursive, force):
    """Background task to run ingestion"""
    try:
        logger.info(f"Starting ingestion of directory: {directory}")
        
        stats = core.ingest_files(
            directory=directory,
            db_path=DEFAULT_DB_PATH,
            model_name=DEFAULT_MODEL,
            provider='ollama',
            recursive=recursive,
            exclude_patterns=[],
            force=force
        )
        
        logger.info(f"Ingestion completed: {stats}")
        
    except Exception as e:
        logger.error(f"Error in background ingestion: {e}")

def create_app(config=None):
    """Application factory"""
    if config:
        app.config.update(config)
    
    return app

def run_server(host='0.0.0.0', port=8080, debug=False, ssl_context=None):
    """Run the Flask development server"""
    logger.info(f"Starting Llamaball Web Server on {host}:{port}")
    logger.info(f"Database: {DEFAULT_DB_PATH}")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    
    if ssl_context:
        logger.info("HTTPS enabled")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        ssl_context=ssl_context,
        request_handler=WSGIRequestHandler
    )

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Llamaball Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--ssl-cert', help='SSL certificate file')
    parser.add_argument('--ssl-key', help='SSL private key file')
    
    args = parser.parse_args()
    
    ssl_context = None
    if args.ssl_cert and args.ssl_key:
        ssl_context = (args.ssl_cert, args.ssl_key)
    
    run_server(
        host=args.host,
        port=args.port,
        debug=args.debug,
        ssl_context=ssl_context
    ) 