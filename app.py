from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import urllib.parse
import time
import os
import boto3
from dotenv import load_dotenv
from deepResearch import DeepResearchAPI

from google import genai
from google.genai import types
from io import BytesIO
import base64
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
# Configure R2
r2 = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY')
)
R2_BUCKET = os.getenv('R2_BUCKET')

# Initialize DeepResearch API client
deep_research_api = DeepResearchAPI(base_url="https://deep-research.qiulanfang.uk")

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


def uploadToR2(image_bytes, content_type='image/png'):
    """
    Upload image bytes to R2 storage and return the public URL
    """
    try:
        # Generate unique filename
        timestamp = int(time.time())
        uuid = os.urandom(8).hex()  # Generate a random 8-byte hex string
        filename = f"{uuid}_{timestamp}.png"
        
        # Upload to R2
        r2.put_object(
            Bucket=R2_BUCKET,
            Key=filename,
            Body=image_bytes,
            ContentType=content_type
        )
        
        # Get public URL
        return f"{os.getenv('R2_PUBLIC_URL')}/{filename}"
    except Exception as e:
        raise Exception(f'Failed to upload image: {str(e)}')

def test_reupload():
    """
    Test function for reupload functionality
    Returns True if test passes, raises Exception if test fails
    """
    try:
        # Create a small test image (1x1 pixel black PNG)
        test_image_bytes = bytes.fromhex('89504e470d0a1a0a0000000d494844520000000100000001080600000001f15c4800000009704859730000000ec300000ec301c76fa864000000134944415478da636460606000000002000001200001f3ff6e4b0000000049454e44ae426082')
        
        # Test uploading with default content type
        url1 = uploadToR2(test_image_bytes)
        if not url1 or not url1.startswith(os.getenv('R2_PUBLIC_URL', '')):
            raise Exception('Default content type test failed')
            
        # Test uploading with custom content type
        url2 = uploadToR2(test_image_bytes, 'image/jpeg')
        if not url2 or not url2.startswith(os.getenv('R2_PUBLIC_URL', '')):
            raise Exception('Custom content type test failed')
            
        return True
        
    except Exception as e:
        raise Exception(f'Reupload test failed: {str(e)}')

@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        print("Prompt:", prompt)
        # Initialize the Gemini client
        inline_data = call_gemini(prompt)
        if not inline_data or not inline_data.data:
            return jsonify({'error': 'Failed to generate image'}), 500
        # Upload the generated image to R2
        image_url = uploadToR2(BytesIO(inline_data.data), content_type='image/png')
        if not image_url:
            return jsonify({'error': 'Failed to upload image to R2'}), 500
        return jsonify({'image_url': image_url})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def call_gemini(prompt, model='gemini-2.0-flash-preview-image-generation'):
    """
    Call the Gemini API with the given prompt and model.
    Returns the response text.
    """
    try:
        contents = (prompt)
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                temperature=0,
                top_p=0.80
            )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                return part.inline_data
    except Exception as e:
        raise Exception(f'Gemini API call failed: {str(e)}')

@app.route('/api/deep_research', methods=['POST'])
def deep_research():
    try:
        # Get required parameters
        query = request.json.get('query')
        provider = request.json.get('provider', 'google')
        thinking_model = request.json.get('thinkingModel', 'gemini-2.0-flash-thinking-exp')
        task_model = request.json.get('taskModel', 'gemini-2.0-flash-exp')
        search_provider = request.json.get('searchProvider', 'model')
        
        # Get optional parameters
        language = request.json.get('language')
        max_result = request.json.get('maxResult')
        enable_citation_image = request.json.get('enableCitationImage')
        enable_references = request.json.get('enableReferences')
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
            
        # Perform the search
        result = deep_research_api.search(
            query=query,
            provider=provider,
            thinking_model=thinking_model,
            task_model=task_model,
            search_provider=search_provider,
            language=language,
            max_result=max_result,
            enable_citation_image=enable_citation_image,
            enable_references=enable_references
        )
        
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    # promt='generate a 1024x500 PNG image for your blog post cover about company financial statements. The image will feature a clean,' \
    # ' modern design incorporating elements like charts, graphs, and possibly a balance sheet or income statement snippet in a visually appealing and professional manner.'
    # inline_data=call_gemini(promt)
    # uploadToR2(BytesIO((inline_data.data)), content_type='image/png')
    # image = Image.open(BytesIO((inline_data.data)))
    # image.save('gemini-native-image.png')
    # image.show()
