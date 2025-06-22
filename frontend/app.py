from flask import Flask, render_template, request, send_file, jsonify
import os
from lmnt import text_to_speech

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_speech():
    try:
        text = request.json.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        output_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp3')
        text_to_speech(text, output_file=output_file)
        
        return jsonify({
            'success': True,
            'audio_url': '/static/audio/output.mp3'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 