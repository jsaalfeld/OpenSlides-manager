from flask import Flask
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
 
@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
     print("Starting WSGI Server on Port 8000")
     server = WSGIServer(('', 8000), app)
     server.serve_forever()
