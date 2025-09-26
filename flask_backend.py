from flask import Flask, render_template, request, jsonify
import os
import sys
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDpZTqY4_93qsWKzrI-WlzQig2DiN04Lkk')
genai.configure(api_key=GEMINI_API_KEY)

model_name = 'gemini-2.0-flash-exp'
print(f"Attempting to initialize model: {model_name}")

try:
    model = genai.GenerativeModel(
        model_name,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 40
        }
    )
    
    print("\nTesting model connection...")
    test_prompt = "Hello, this is a test connection. Please respond with 'Connection successful!'"
    test_response = model.generate_content(test_prompt)
    
    if hasattr(test_response, 'text'):
        print(f"Model initialized successfully!")
except Exception as e:
    print(f"\nError initializing Gemini model: {str(e)}")

@app.route('/')
def index():
    return render_template('html_template.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-api-key-here':
            return jsonify({
                'error': 'API key not properly configured. Please set the GEMINI_API_KEY environment variable.',
                'status': 'error'
            }), 500

        if not request.is_json:
            return jsonify({'error': 'Request must be JSON', 'status': 'error'}), 400
            
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided', 'status': 'error'}), 400
        
        try:
            response = model.generate_content(user_message)
            
            if not response or not hasattr(response, 'text'):
                error_details = {
                    'error': 'Invalid response from AI model',
                    'status': 'error',
                    'response_attrs': dir(response) if hasattr(response, '__dict__') else 'No attributes'
                }
                print(f"Invalid response details: {error_details}")
                return jsonify(error_details), 500
                
            ai_response = response.text
            
            return jsonify({
                'response': ai_response,
                'status': 'success'
            })
            
        except Exception as genai_error:
            print(f"Gemini API Error: {str(genai_error)}")
            return jsonify({
                'error': f'Error from Gemini API: {str(genai_error)}',
                'status': 'error'
            }), 500
    
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({
            'error': f'Server error: {str(e)}',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Flask chatbot server...")
    print("📱 Open http://127.0.0.1:5000/ in your browser")
    app.run(debug=True, host='127.0.0.1', port=5000)