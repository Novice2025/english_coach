from flask import Flask
import os

# We define 'app' globally so Gunicorn can find it easily
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_123'

@app.route('/')
def home():
    return "<h1>VISHULCOACH IS ONLINE</h1><p>The core engine is working.</p>"

# This is for local testing, Render uses the 'app' object above
if __name__ == '__main__':
    app.run(debug=True)
