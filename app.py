from flask import Flask, render_template, request, redirect, url_for
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'wav', 'mp3'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create the upload directory if it doesn't exist
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            command = f"whisper '{file_path}' --model large"
            process = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            output = process.stdout
            lines = output.split('\n')
            timestamps = []
            texts = []
            for line in lines:
                if '] ' in line:
                    timestamp, text = line.split('] ', 1)
                    timestamp = timestamp[1:]
                    timestamps.append(timestamp)
                    texts.append(text)
            text_string = ' '.join(texts)
            return render_template('result.html', transcript=text_string)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)