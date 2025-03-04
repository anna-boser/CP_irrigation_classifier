import http.server
import socketserver

#Change Directory to Folder with RGB Images and Run Code
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

PORT = 8000
with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
