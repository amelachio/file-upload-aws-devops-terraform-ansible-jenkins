from flask import Flask, render_template, request, redirect, url_for
import requests

import config

app = Flask(__name__)


@app.route('/')
def index():
    try:
        response = requests.get(f"{config.BACKEND_URL}/files", timeout=5)
        files = response.json().get('files', [])
    except requests.RequestException:
        files = []

    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('index'))

    files = {'file': (file.filename, file.stream, file.mimetype)}

    try:
        requests.post(f"{config.BACKEND_URL}/upload", files=files, timeout=10)
    except requests.RequestException:
        pass

    return redirect(url_for('index'))


@app.route('/delete/<int:file_id>', methods=['POST'])
def delete(file_id):
    try:
        requests.delete(f"{config.BACKEND_URL}/files/{file_id}", timeout=5)
    except requests.RequestException:
        pass

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
