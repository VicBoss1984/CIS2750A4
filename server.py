import molsql
import MolDisplay
import sys # this import is necessary for using any methods from the system module
import urllib # I need this import for parsing the web content
from http.server import HTTPServer, BaseHTTPRequestHandler # I needed this import for the webserver
from io import BytesIO # just like MolDisplay.py, I can't think of another implementation that would work without the io module

# frontendFiles = ['/frontEnd/cssSrc/css_file1.css', '/frontEnd/htmlSrc/htmlWebsite.html', '/frontend/javascriptSrc/javascript_code.js']

# customHandler is a class that inherits the BaseHTTPRequestHandler class
class customHandler(BaseHTTPRequestHandler):
	
	# do_GET method has been overriden because I wanted to customize what the webserver shows when it starts running
	def do_GET(self):
		print(f"Requested path: {self.path}")
		if self.path == "/":
			self.path = "/frontEnd/htmlSrc/htmlWebsite.html"
		contentType = None
		if self.path.endswith(".html"):
			contentType = "text/html"
		elif self.path.endswith(".css"):
			contentType = "text/css"
		elif self.path.endswith(".js"):
			contentType = "application/javascript"

		if contentType:
			try:
				with open(self.path[1:], "r") as f:
					page = f.read()
					self.send_response(200)
					self.send_header("Content-type", contentType)
					self.send_header("Content-length", len(page))
					self.end_headers()
					self.wfile.write(bytes(page, "utf-8"))
			except FileNotFoundError:
				print(f"File not found: {self.path[1:]}")
				self.send_response(404)
				self.end_headers()
				self.wfile.write(bytes("404: not found", "utf-8"))
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write(bytes("404: not found", "utf-8"))

	# do_POST method needed to be overriden because I needed to perform specific computations and library calls to make it useful
	def do_POST(self):
		if self.path == "/molecule":
			contentLength = int(self.headers['Content-Length'])
			body = self.rfile.read(contentLength)
			body = BytesIO(body)
			molIns = MolDisplay.Molecule()
			parsedFile = molIns.parse(body)
			if parsedFile is not None:
				molIns.sort()
				svgData = molIns.svg()
				self.send_response(200)
				self.send_header('Content-type', 'image/svg+xml')
				self.end_headers()
				self.wfile.write(svgData.encode('utf-8'))
			else:
				self.send_error(400, message = "Error parsing the file")
		else:
			self.send_error(404)

# Taking command-line arguments here, which is where the sys module comes in!
httpd = HTTPServer(('localhost', int(sys.argv[1])), customHandler)
httpd.serve_forever()