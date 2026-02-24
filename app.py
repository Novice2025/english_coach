from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>VISHULCOACH IS ONLINE</h1><p>The core engine is working.</p>"

if __name__ == '__main__':
    app.run(debug=True)
