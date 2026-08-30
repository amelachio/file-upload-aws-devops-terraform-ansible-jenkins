from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, Response
import requests

import config

app = Flask(__name__)


@app.route('/')
def index():
    try:
        response = requests.get(f"{config.BACKEND_URL}/files", timeout=5)
        files = response.json().get('files', [])
        for f in files:
            f['download_link'] = f"/download?url={quote(f['url'])}&name={quote(f['filename'])}"
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

@app.route('/rename/<int:file_id>', methods=['POST'])
def rename(file_id):
    new_name = request.form.get('new_name')

    if not new_name:
        return redirect(url_for('index'))

    try:
        requests.put(
            f"{config.BACKEND_URL}/files/{file_id}",
            json={'filename': new_name},
            timeout=5
        )
    except requests.RequestException:
        pass

    return redirect(url_for('index'))


@app.route('/download')
def download():
    file_url = request.args.get('url')
    filename = request.args.get('name', 'file')

    if not file_url:
        return redirect(url_for('index'))

    try:
        r = requests.get(file_url, stream=True, timeout=10)
    except requests.RequestException:
        return redirect(url_for('index'))

    return Response(
        r.iter_content(chunk_size=8192),
        content_type=r.headers.get('Content-Type', 'application/octet-stream'),
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )
