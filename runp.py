#!flask/bin/python

import sys

from app import app


port = 5000
print sys.argv

if len(sys.argv) >= 2:
	port = int(sys.argv[1])

app.run(debug=False, threaded=True, port=port)
