#!/usr/bin/env python3
"""
Debug Flask App - Minimal test
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head><title>Debug Test</title></head>
    <body style="font-family: Arial; padding: 50px;">
        <h1 style="color: green;">✅ Flask is Working!</h1>
        <p>If you can see this page, Flask is running correctly.</p>
        <p><strong>Time:</strong> <span id="time"></span></p>
        <p><a href="/test">Test another page</a></p>
        
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return '<h1>Test page works!</h1><a href="/">Back to main</a>'

if __name__ == '__main__':
    print("🔍 Starting DEBUG Flask app...")
    print("Visit: http://localhost:5001")
    print("If you see a blank page, there's a browser or network issue")
    app.run(debug=True, host='0.0.0.0', port=5001)