import uuid
from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
import pymysql

import config

app = Flask(__name__)

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
CLOUDFRONT_DOMAIN = "dysbwhhaii6i9.cloudfront.net"

s3_client = boto3.client('s3', region_name=config.S3_REGION)


def get_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    file_type = file.mimetype
    if file_type not in ALLOWED_TYPES:
        return jsonify({'error': 'File type not allowed'}), 400

    original_name = file.filename
    s3_key = f"{uuid.uuid4()}-{original_name}"

    try:
        s3_client.upload_fileobj(
            file,
            config.S3_BUCKET,
            s3_key,
            ExtraArgs={'ContentType': file_type}
        )
    except ClientError:
        return jsonify({'error': 'S3 upload failed'}), 500

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO files (original_name, s3_key, file_type, uploaded_at) VALUES (%s, %s, %s, NOW())",
                (original_name, s3_key, file_type)
            )
        connection.commit()
        connection.close()
    except pymysql.MySQLError:
        return jsonify({'error': 'Database error'}), 500

    return jsonify({
        'success': True,
        'filename': original_name,
        's3_key': s3_key
    })


@app.route('/files', methods=['GET'])
def list_files():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, original_name, s3_key, file_type, uploaded_at FROM files ORDER BY uploaded_at DESC"
            )
            rows = cursor.fetchall()
        connection.close()
    except pymysql.MySQLError:
        return jsonify({'error': 'Database error'}), 500

    files = [
        {
            'id': row[0],
            'filename': row[1],
            'url': f"https://{CLOUDFRONT_DOMAIN}/{row[2]}",
            'file_type': row[3],
            'uploaded_at': row[4].isoformat()
        }
        for row in rows
    ]

    return jsonify({'files': files})


@app.route('/files/<int:file_id>', methods=['PUT'])
def update_file(file_id):
    data = request.get_json(silent=True)

    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing filename'}), 400

    new_name = data['filename']

    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT original_name FROM files WHERE id = %s", (file_id,))
            row = cursor.fetchone()
            if row is None:
                connection.close()
                return jsonify({'error': 'File not found'}), 404

            old_name = row[0]
            if '.' in old_name and '.' not in new_name:
                extension = old_name.rsplit('.', 1)[1]
                new_name = f"{new_name}.{extension}"

            cursor.execute(
                "UPDATE files SET original_name = %s WHERE id = %s",
                (new_name, file_id)
            )
        connection.commit()
        connection.close()
    except pymysql.MySQLError:
        return jsonify({'error': 'Database error'}), 500

    return jsonify({'success': True, 'id': file_id, 'new_filename': new_name})


@app.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT s3_key FROM files WHERE id = %s", (file_id,))
            row = cursor.fetchone()

            if row is None:
                connection.close()
                return jsonify({'error': 'File not found'}), 404

            s3_key = row[0]

            try:
                s3_client.delete_object(Bucket=config.S3_BUCKET, Key=s3_key)
            except ClientError:
                connection.close()
                return jsonify({'error': 'S3 deletion failed'}), 500

            cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
        connection.commit()
        connection.close()
    except pymysql.MySQLError:
        return jsonify({'error': 'Database error'}), 500

    return jsonify({'success': True, 'deleted_id': file_id})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
