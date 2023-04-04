import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import MolDisplay

class customHandler(BaseHTTPRequestHandler):
	
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

httpd = HTTPServer(('localhost', int(sys.argv[1])), customHandler)
httpd.serve_forever()