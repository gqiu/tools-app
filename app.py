from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import urllib.parse
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/quote', methods=['POST'])
def quote():
    text = request.json.get('text', '')
    # First escape any existing escaped sequences
    text = text.replace('\\', '\\\\')
    # Then escape quotes
    text = text.replace('"', '\\"')
    # Add outer quotes
    result = f'"{text}"'
    return jsonify({'result': result})

@app.route('/api/unquote', methods=['POST'])
def unquote():
    text = request.json.get('text', '')
    if not (text.startswith('"') and text.endswith('"')):
        return jsonify({'result': text})
    
    # Remove outer quotes
    text = text[1:-1]
    
    # First unescape quotes
    text = text.replace('\\"', '"')
    # Then unescape backslashes
    text = text.replace('\\\\', '\\')
    
    return jsonify({'result': text})

@app.route('/api/remove_extra_spaces', methods=['POST'])
def remove_extra_spaces():
    text = request.json.get('text', '')
    result = ' '.join(text.split())
    return jsonify({'result': result})

@app.route('/api/remove_whitespace', methods=['POST'])
def remove_whitespace():
    text = request.json.get('text', '')
    result = ''.join(text.split())
    return jsonify({'result': result})

@app.route('/api/base64_encode', methods=['POST'])
def base64_encode():
    text = request.json.get('text', '')
    result = base64.b64encode(text.encode()).decode()
    return jsonify({'result': result})

@app.route('/api/base64_decode', methods=['POST'])
def base64_decode():
    try:
        text = request.json.get('text', '')
        result = base64.b64decode(text.encode()).decode()
        return jsonify({'result': result})
    except:
        return jsonify({'result': 'Invalid Base64 string'})

@app.route('/api/url_encode', methods=['POST'])
def url_encode():
    text = request.json.get('text', '')
    result = urllib.parse.quote(text)
    return jsonify({'result': result})

@app.route('/api/url_decode', methods=['POST'])
def url_decode():
    try:
        text = request.json.get('text', '')
        result = urllib.parse.unquote(text)
        return jsonify({'result': result})
    except:
        return jsonify({'result': 'Invalid URL encoded string'})

@app.route('/api/timestamp_to_mst', methods=['POST'])
def timestamp_to_mst():
    try:
        timestamp = int(request.json.get('text', '0'))
        result = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))
        return jsonify({'result': result})
    except:
        return jsonify({'result': 'Invalid timestamp'})

@app.route('/api/mst_to_timestamp', methods=['POST'])
def mst_to_timestamp():
    try:
        text = request.json.get('text', '')
        time_struct = time.strptime(text, '%Y-%m-%d %H:%M:%S')
        result = str(int(time.mktime(time_struct) * 1000))
        return jsonify({'result': result})
    except:
        return jsonify({'result': 'Invalid datetime format (Use: YYYY-MM-DD HH:MM:SS)'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
