#!/usr/bin/env python3
import os
import json
import hashlib
import datetime
import mimetypes
import uuid
import cgi
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import secrets
import time

# Configuration
UPLOAD_DIR = 'static/uploads'
DATA_FILE = 'files.json'
SETTINGS_FILE = 'settings.json'
ALLOWED_EXTENSIONS_FILE = 'allowed_extensions.json'

# Default credentials
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'

# Default allowed extensions
DEFAULT_ALLOWED_EXTENSIONS = [
    'pdf', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3', 'webm',
    'zip', 'rar', '7z', 'tar', 'gz', 'txt', 'md',
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'csv', 'json', 'xml', 'html', 'css', 'js'
]

# Store active sessions
active_sessions = {}
SESSION_TIMEOUT = 24 * 60 * 60

def cleanup_expired_sessions():
    now = time.time()
    expired = []
    for sid, data in active_sessions.items():
        if now - data.get('created_at_ts', 0) > SESSION_TIMEOUT:
            expired.append(sid)
    for sid in expired:
        del active_sessions[sid]

def load_allowed_extensions():
    if os.path.exists(ALLOWED_EXTENSIONS_FILE):
        try:
            with open(ALLOWED_EXTENSIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_ALLOWED_EXTENSIONS.copy()
    return DEFAULT_ALLOWED_EXTENSIONS.copy()

def save_allowed_extensions(extensions):
    with open(ALLOWED_EXTENSIONS_FILE, 'w') as f:
        json.dump(extensions, f, indent=2)

def is_safe_extension(filename, allowed_exts):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return ext in allowed_exts

def sanitize_filename(filename):
    filename = os.path.basename(filename)
    dangerous = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    for d in dangerous:
        filename = filename.replace(d, '')
    safe = ''.join(c for c in filename if c.isalnum() or c in '.-_ ')
    safe = safe.strip()
    if len(safe) > 200:
        name, ext = os.path.splitext(safe)
        safe = name[:200 - len(ext)] + ext
    return safe if safe else 'unnamed_file'

def detect_mime(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    mime_map = {
        'pdf': 'application/pdf', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'png': 'image/png', 'gif': 'image/gif', 'mp4': 'video/mp4',
        'mp3': 'audio/mpeg', 'zip': 'application/zip', 'txt': 'text/plain',
        'html': 'text/html', 'css': 'text/css', 'js': 'application/javascript',
        'json': 'application/json', 'csv': 'text/csv'
    }
    return mime_map.get(ext, 'application/octet-stream')

class UploadCenterHandler(SimpleHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.serve_html('templates/index.html')
        elif parsed.path == '/admin':
            self.serve_admin()
        elif parsed.path == '/login.html':
            self.serve_html('templates/login.html')
        elif parsed.path == '/logout':
            self.handle_logout()
        elif parsed.path == '/api/files':
            self.serve_public_files()
        elif parsed.path == '/api/files/all':
            self.serve_all_files()
        elif parsed.path == '/api/settings':
            self.serve_settings()
        elif parsed.path == '/api/check-auth':
            self.check_auth()
        elif parsed.path == '/api/allowed-extensions':
            self.serve_allowed_extensions()
        elif parsed.path.startswith('/download/'):
            self.serve_file_download()
        elif parsed.path.startswith('/static/'):
            super().do_GET()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/upload':
            self.handle_upload()
        elif self.path == '/api/login':
            self.handle_login()
        else:
            self.send_error(404)
    
    def do_PUT(self):
        if self.path == '/api/settings':
            self.handle_settings_update()
        elif self.path == '/api/security-settings':
            self.handle_security_update()
        elif self.path == '/api/allowed-extensions':
            self.handle_allowed_extensions_update()
        elif self.path.startswith('/api/visibility/'):
            self.handle_visibility()
        elif self.path.startswith('/api/showonhome/'):
            self.handle_show_on_home()
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        if self.path.startswith('/api/delete/'):
            self.handle_delete()
        else:
            self.send_error(404)
    
    def get_session(self):
        cookie = self.headers.get('Cookie', '')
        for item in cookie.split(';'):
            item = item.strip()
            if item.startswith('session='):
                return item.split('=')[1]
        return None
    
    def set_session(self, session_id):
        self.send_header('Set-Cookie', f'session={session_id}; Path=/; HttpOnly; Max-Age={SESSION_TIMEOUT}')
    
    def clear_session(self):
        self.send_header('Set-Cookie', 'session=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT')
    
    def is_auth(self):
        cleanup_expired_sessions()
        sid = self.get_session()
        return sid and sid in active_sessions
    
    def serve_admin(self):
        if not self.is_auth():
            self.send_response(302)
            self.send_header('Location', '/login.html')
            self.end_headers()
            return
        self.serve_html('templates/admin.html')
    
    def check_auth(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'auth': self.is_auth()}).encode())
    
    def handle_login(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        
        username = data.get('username', '')
        password = data.get('password', '')
        
        settings = self.load_settings()
        stored_user = settings.get('username', DEFAULT_USERNAME)
        stored_pass = settings.get('password', DEFAULT_PASSWORD)
        
        if username == stored_user and password == stored_pass:
            sid = secrets.token_hex(32)
            active_sessions[sid] = {
                'username': username,
                'created_at_ts': time.time()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.set_session(sid)
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode())
    
    def handle_logout(self):
        sid = self.get_session()
        if sid in active_sessions:
            del active_sessions[sid]
        
        self.send_response(302)
        self.send_header('Location', '/')
        self.clear_session()
        self.end_headers()
    
    def serve_public_files(self):
        files = self.load_files()
        public = [f for f in files if f.get('visibility') == 'public' and f.get('show_on_home', False)]
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(public).encode())
    
    def serve_all_files(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        files = self.load_files()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(files).encode())
    
    def serve_settings(self):
        settings = self.load_settings()
        response = {
            'max_file_size_mb': settings.get('max_file_size_mb', 100),
            'username': settings.get('username', DEFAULT_USERNAME),
            'site_name': settings.get('site_name', 'FileCenter'),
            'site_description': settings.get('site_description', 'Secure file sharing platform')
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def serve_allowed_extensions(self):
        exts = load_allowed_extensions()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'extensions': exts}).encode())
    
    def handle_settings_update(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        
        if 'max_file_size_mb' in data:
            settings = self.load_settings()
            settings['max_file_size_mb'] = max(1, min(2048, int(data['max_file_size_mb'])))
            self.save_settings(settings)
            
        if 'site_name' in data:
            settings = self.load_settings()
            settings['site_name'] = data['site_name'][:100]
            self.save_settings(settings)
            
        if 'site_description' in data:
            settings = self.load_settings()
            settings['site_description'] = data['site_description'][:500]
            self.save_settings(settings)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def handle_security_update(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        
        settings = self.load_settings()
        
        if 'username' in data and data['username']:
            user = ''.join(c for c in data['username'] if c.isalnum() or c in '._-')
            if len(user) >= 3:
                settings['username'] = user
        
        if 'password' in data and data['password']:
            if len(data['password']) >= 4:
                settings['password'] = data['password']
        
        self.save_settings(settings)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def handle_allowed_extensions_update(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        
        if 'extensions' in data:
            exts = [e.strip().lower() for e in data['extensions'] if e.strip()]
            if exts:
                save_allowed_extensions(exts)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def serve_file_download(self):
        fid = self.path.split('/')[-1]
        files = self.load_files()
        
        for f in files:
            if f['id'] == fid:
                is_admin = self.is_auth()
                if f.get('visibility') == 'private' and not is_admin:
                    self.send_error(403)
                    return
                
                path = os.path.join(UPLOAD_DIR, f['filename'])
                if os.path.exists(path):
                    f['downloads'] = f.get('downloads', 0) + 1
                    self.save_files(files)
                    
                    self.send_response(200)
                    mime = detect_mime(f['original_name'])
                    encoded = urllib.parse.quote(f['original_name'])
                    self.send_header('Content-type', mime)
                    self.send_header('Content-Disposition', f'attachment; filename*=UTF-8\'\'{encoded}')
                    self.send_header('Content-Length', str(f['size']))
                    self.end_headers()
                    
                    with open(path, 'rb') as fh:
                        while True:
                            chunk = fh.read(8192)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                    return
        
        self.send_error(404)
    
    def handle_upload(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        settings = self.load_settings()
        max_size = settings.get('max_file_size_mb', 100) * 1024 * 1024
        allowed_exts = load_allowed_extensions()
        
        try:
            # Parse multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers.get('Content-Type', '')}
            )
        except Exception as e:
            self.send_error(400, f'Error parsing form data: {str(e)}')
            return
        
        if 'file' not in form:
            self.send_error(400, 'No file field in form')
            return
        
        file_item = form['file']
        if not file_item.filename:
            self.send_error(400, 'No file selected')
            return
        
        # Read file content
        try:
            content = file_item.file.read()
        except Exception as e:
            self.send_error(500, f'Error reading file: {str(e)}')
            return
        
        # Sanitize filename
        original = sanitize_filename(file_item.filename)
        
        # Check extension
        if not is_safe_extension(original, allowed_exts):
            self.send_error(400, f'File type not allowed. Allowed: {", ".join(allowed_exts)}')
            return
        
        # Check file size
        size = len(content)
        if size > max_size:
            self.send_error(413, f'File exceeds {settings["max_file_size_mb"]} MB limit')
            return
        
        # Get visibility settings
        visibility = form.getvalue('visibility', 'private')
        show_home = form.getvalue('show_on_home', 'false') == 'true'
        
        # If show_home is true, visibility must be public
        if show_home:
            visibility = 'public'
        
        # Create unique filename
        ext = os.path.splitext(original)[1].lower()
        unique = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique)
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
        except Exception as e:
            self.send_error(500, f'Error saving file: {str(e)}')
            return
        
        # Generate file ID
        fid = hashlib.sha256(f"{unique}{time.time()}{secrets.token_hex(4)}".encode()).hexdigest()[:16]
        
        # Save to database
        files = self.load_files()
        files.append({
            'id': fid,
            'original_name': original,
            'name': original,
            'filename': unique,
            'size': size,
            'uploaded_at': datetime.datetime.now().isoformat(),
            'downloads': 0,
            'visibility': visibility,
            'show_on_home': show_home
        })
        self.save_files(files)
        
        # Send success response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True, 'id': fid}).encode())
    
    def handle_visibility(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        fid = self.path.split('/')[-1]
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        new_vis = data.get('visibility')
        
        if new_vis not in ['public', 'private']:
            self.send_error(400)
            return
        
        files = self.load_files()
        for f in files:
            if f['id'] == fid:
                f['visibility'] = new_vis
                if new_vis == 'private':
                    f['show_on_home'] = False
                self.save_files(files)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'visibility': new_vis, 'show_on_home': f['show_on_home']}).encode())
                return
        
        self.send_error(404)
    
    def handle_show_on_home(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        fid = self.path.split('/')[-1]
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        show = data.get('show_on_home', False)
        
        files = self.load_files()
        for f in files:
            if f['id'] == fid:
                if f.get('visibility') == 'public':
                    f['show_on_home'] = show
                    self.save_files(files)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True, 
                        'show_on_home': f['show_on_home'],
                        'visibility': f['visibility']
                    }).encode())
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False, 
                        'error': 'Cannot enable show on home for private file. Make file public first.'
                    }).encode())
                return
        
        self.send_error(404)
    
    def handle_delete(self):
        if not self.is_auth():
            self.send_response(401)
            self.end_headers()
            return
        
        fid = self.path.split('/')[-1]
        files = self.load_files()
        
        for i, f in enumerate(files):
            if f['id'] == fid:
                path = os.path.join(UPLOAD_DIR, f['filename'])
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
                del files[i]
                self.save_files(files)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
                return
        
        self.send_error(404)
    
    def serve_html(self, path):
        try:
            with open(path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)
        except Exception as e:
            self.send_error(500, str(e))
    
    def load_files(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                files = json.load(f)
                for f in files:
                    if 'visibility' not in f:
                        f['visibility'] = 'private'
                    if 'show_on_home' not in f:
                        f['show_on_home'] = False
                return files
        except:
            return []
    
    def save_files(self, files):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(files, f, indent=2, ensure_ascii=False)
    
    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return {
                'max_file_size_mb': 100,
                'username': DEFAULT_USERNAME,
                'password': DEFAULT_PASSWORD,
                'site_name': 'FileCenter',
                'site_description': 'Secure, fast, and reliable file sharing platform'
            }
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                'max_file_size_mb': 100,
                'username': DEFAULT_USERNAME,
                'password': DEFAULT_PASSWORD,
                'site_name': 'FileCenter',
                'site_description': 'Secure, fast, and reliable file sharing platform'
            }
    
    def save_settings(self, settings):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)

def run_server(port=3000):
    # Create directories
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Initialize data file
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)
    
    # Initialize settings file
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'max_file_size_mb': 100,
                'username': DEFAULT_USERNAME,
                'password': DEFAULT_PASSWORD,
                'site_name': 'FileCenter',
                'site_description': 'Secure, fast, and reliable file sharing platform'
            }, f, indent=2)
    
    # Initialize allowed extensions file
    if not os.path.exists(ALLOWED_EXTENSIONS_FILE):
        with open(ALLOWED_EXTENSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_ALLOWED_EXTENSIONS, f, indent=2)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    server = HTTPServer(('0.0.0.0', port), UploadCenterHandler)
    
    print("=" * 60)
    print("🚀 FileCenter v2.2 - Server Started")
    print("=" * 60)
    print(f"📡 Port: {port}")
    print(f"🌐 Address: http://localhost:{port}")
    print(f"🔧 Admin: http://localhost:{port}/admin")
    print(f"👤 Username: {DEFAULT_USERNAME}")
    print(f"🔑 Password: {DEFAULT_PASSWORD}")
    print("=" * 60)
    print("✨ Features v2.2:")
    print("✓ File upload - working")
    print("✓ Show on home toggle - fixed (click on slider works)")
    print("✓ Copy link - working")
    print("✓ Private files: toggle disabled")
    print("✓ Public files: toggle works")
    print("✓ Fully responsive")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

if __name__ == '__main__':
    run_server()
