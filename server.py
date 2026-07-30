import http.server
import json
import os
import uuid
import cgi
import urllib.request

PORT = 8000

def upload_to_catbox(file_bytes, filename):
    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    data = []
    
    data.append(f'--{boundary}')
    data.append('Content-Disposition: form-data; name="reqtype"')
    data.append('')
    data.append('fileupload')
    
    data.append(f'--{boundary}')
    data.append(f'Content-Disposition: form-data; name="fileToUpload"; filename="{filename}"')
    mime = 'image/jpeg'
    if filename.lower().endswith('.png'):
        mime = 'image/png'
    data.append(f'Content-Type: {mime}')
    data.append('')
    
    body = b''
    for part in data:
        body += part.encode('utf-8') + b'\r\n'
    
    body += file_bytes + b'\r\n'
    body += f'--{boundary}--\r\n'.encode('utf-8')
    
    req = urllib.request.Request(
        'https://catbox.moe/user/api.php',
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'User-Agent': 'Mozilla/5.0'
        }
    )
    
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8').strip()
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS & Cache control
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/recipes':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            recipes_file = os.path.join(DIRECTORY, 'recipes.json')
            if os.path.exists(recipes_file):
                with open(recipes_file, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'[]')
        else:
            # Let SimpleHTTPRequestHandler serve files from the directory it was started in
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/recipes':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                recipes_data = json.loads(post_data.decode('utf-8'))
                recipes_file = os.path.join(DIRECTORY, 'recipes.json')
                with open(recipes_file, 'w', encoding='utf-8') as f:
                    json.dump(recipes_data, f, ensure_ascii=False, indent=2)
                
                # Update app.js DEFAULT_RECIPES variable directly to stay synchronized
                app_js_path = os.path.join(DIRECTORY, 'app.js')
                if os.path.exists(app_js_path):
                    with open(app_js_path, 'r', encoding='utf-8') as f:
                        app_js_content = f.read()
                    import re
                    recipes_js_str = json.dumps(recipes_data, indent=2, ensure_ascii=False)
                    match = re.search(r'const DEFAULT_RECIPES = \[[\s\S]*?\];', app_js_content)
                    if match:
                        start, end = match.span()
                        new_content = app_js_content[:start] + f"const DEFAULT_RECIPES = {recipes_js_str};" + app_js_content[end:]
                        with open(app_js_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))

        elif self.path == '/api/upload-image':
            try:
                # Use standard cgi.FieldStorage for robust multipart parsing
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                             'CONTENT_TYPE': self.headers['Content-Type']}
                )
                
                if 'image' in form:
                    file_item = form['image']
                    if file_item.file:
                        file_data = file_item.file.read()
                        
                         # Generate unique filename and save locally as backup
                        filename = f"custom_{uuid.uuid4().hex[:10]}.jpg"
                        images_dir = os.path.join(DIRECTORY, 'images')
                        os.makedirs(images_dir, exist_ok=True)
                        filepath = os.path.join(images_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(file_data)
                        
                        # Upload to Catbox for permanent global access
                        cloud_url = upload_to_catbox(file_data, filename)
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "success", "imagePath": cloud_url}).encode('utf-8'))
                        return
                
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'No image field found in form data')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        elif self.path == '/api/publish':
            try:
                import subprocess
                # Stage recipes.json
                subprocess.run(['git', 'add', 'recipes.json'], check=True)
                
                # Check if there are changes to commit
                status_res = subprocess.run(['git', 'status', '--porcelain', 'recipes.json'], capture_output=True, text=True)
                if status_res.stdout.strip():
                    subprocess.run(['git', 'commit', '-m', 'Update recipes from web panel'], check=True)
                
                # Push to remote GitHub repo
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                return
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
                return
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, CustomHandler)
    print(f"Starting custom python server on port {PORT} serving {DIRECTORY}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
