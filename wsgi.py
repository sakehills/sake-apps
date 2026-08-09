import os
import sys
import io
import http.client

# ディレクトリパスの設定とカレントディレクトリの移動
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import SakeApiServer

STATUS_CODES = http.client.responses

def application(environ, start_response):
    """
    PythonAnywhere などの WSGI サーバー環境で server.py の SakeApiServer を動作させるための WSGI ラッパー
    """
    path = environ.get('PATH_INFO', '')
    query = environ.get('QUERY_STRING', '')
    if query:
        path += '?' + query

    method = environ.get('REQUEST_METHOD', 'GET')

    status_box = {'code': 200, 'message': 'OK'}
    headers_box = []
    headers_sent = False

    wfile = io.BytesIO()
    rfile = environ.get('wsgi.input', io.BytesIO())

    class WSGIAdapterHandler(SakeApiServer):
        def __init__(self):
            self.rfile = rfile
            self.wfile = wfile
            self.path = path
            self.command = method
            self.requestline = f"{method} {path} HTTP/1.1"
            self.client_address = (environ.get('REMOTE_ADDR', '127.0.0.1'), 80)
            self.directory = BASE_DIR
            self.server = None

            # WSGI の environ から HTTP ヘッダーを生成
            from http.client import HTTPMessage
            self.headers = HTTPMessage()
            for k, v in environ.items():
                if k.startswith('HTTP_'):
                    h_name = k[5:].replace('_', '-').title()
                    self.headers.add_header(h_name, v)
                elif k in ('CONTENT_TYPE', 'CONTENT_LENGTH') and v:
                    h_name = k.replace('_', '-').title()
                    self.headers.add_header(h_name, v)

        def send_response(self, code, message=None):
            status_box['code'] = code
            status_box['message'] = message or STATUS_CODES.get(code, 'OK')

        def send_header(self, keyword, value):
            headers_box.append((keyword, value))

        def end_headers(self):
            nonlocal headers_sent
            if not headers_sent:
                status_str = f"{status_box['code']} {status_box['message']}"
                start_response(status_str, headers_box)
                headers_sent = True

        def send_error(self, code, message=None, explain=None):
            status_box['code'] = code
            status_box['message'] = message or STATUS_CODES.get(code, 'Error')
            headers_box.clear()
            headers_box.append(('Content-Type', 'text/html; charset=utf-8'))
            self.end_headers()
            wfile.write(f"<h1>{code} {status_box['message']}</h1>".encode('utf-8'))

    handler = WSGIAdapterHandler()

    try:
        if method == 'GET':
            handler.do_GET()
        elif method == 'POST':
            handler.do_POST()
        elif method == 'OPTIONS':
            if hasattr(handler, 'do_OPTIONS'):
                handler.do_OPTIONS()
            else:
                handler.send_response(200)
                handler.send_header('Access-Control-Allow-Origin', '*')
                handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
                handler.end_headers()
        else:
            handler.send_error(405, "Method Not Allowed")
    except Exception as e:
        import traceback
        traceback.print_exc()
        if not headers_sent:
            handler.send_error(500, f"Internal Server Error: {str(e)}")

    if not headers_sent:
        handler.end_headers()

    return [wfile.getvalue()]
