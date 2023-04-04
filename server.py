import sys # this import is necessary for using any methods from the system module
from http.server import HTTPServer, BaseHTTPRequestHandler # I needed this import for the webserver
from urllib.parse import urlparse, parse_qs # I need this import for parsing the web content
from io import BytesIO # just like MolDisplay.py, I can't think of another implementation that would work without the io module
import MolDisplay # I need MolDisplay to use my own python library

# customHandler is a class that inherits the BaseHTTPRequestHandler class
class customHandler(BaseHTTPRequestHandler):
	
	# do_GET method has been overriden because I wanted to customize what the webserver shows when it starts running
	def do_GET(self):
		if self.path == "/":
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.send_header("Content-length", len(webform))
			self.end_headers()
			self.wfile.write(bytes(webform, "utf-8"))
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

# Embedded html code for my do_GET method
webform = """ 
<html>
	<head>
		<title> File Upload </title>
	</head>
	<body>
		<h1> File Upload </h1>
		<form action="molecule" enctype="multipart/form-data" method="post">
			<p>
				<input type="file" id="sdf_file" name="filename"/>
			</p>
			<p>
				<input type="submit" value="Upload"/>
			</p>
	   </form>
	 </body>
</html> 
"""

# Taking command-line arguments here, which is where the sys module comes in!
httpd = HTTPServer(('localhost', int(sys.argv[1])), customHandler)
httpd.serve_forever()