from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_123'

@app.route('/')
def home():
    return "<h1>VISHULCOACH IS ONLINE</h1><p>If you see this, the server is fixed.</p>"

if __name__ == '__main__':
    app.run(debug=True)
