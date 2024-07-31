from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
import os
import requests
import boto3 

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        # Read the original file data
        file_data = file.read()
        
        # Generate a new filename with the same extension
        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1]
        custom_id = str(uuid.uuid4())
        new_filename = custom_id + extension

        # Upload the file to S3
        s3_url = upload_to_s3(file_data, new_filename, file.content_type)
        
        if not s3_url:
            return render_template('error.html', error_message="Failed to upload to S3")
        
        # Invoke Lambda via API Gateway with the S3 URL
        response = requests.post(
            'https://jv16aedy33.execute-api.us-east-1.amazonaws.com/Prod/upload',
            json={'imageUrl': s3_url},
            headers={'Content-Type': 'application/json'}
        )
        
        # Get the result from Lambda
        result = response.json()
        
        # Check for errors in the result
        if response.status_code != 200 or 'error' in result:
            error_message = result.get('error', 'Unknown error occurred')
            return render_template('error.html', error_message=error_message)
        
        # Handle the inference result
        inference_result = result.get('inference', 'No inference result returned')
        
        # Pass the result to the result page
        return redirect(url_for('result', filename=custom_id, inference=inference_result))
    
    # Redirect to index if no file was processed
    return redirect(url_for('index'))
    
@app.route('/result')
def result():
    filename = request.args.get('filename')
    inference = request.args.get('inference', 'No inference result')
    return render_template('result.html', filename=filename, inference=inference)

def upload_to_s3(file_data, filename, content_type):
    import boto3
    from botocore.exceptions import NoCredentialsError

    s3 = boto3.client('s3')
    bucket_name = '2303826xrayimages'

    try:
        s3.put_object(Bucket=bucket_name, Key=f'uploads/{filename}', Body=file_data, ContentType=content_type)
        s3_url = f'https://{bucket_name}.s3.amazonaws.com/uploads/{filename}'
        return s3_url
    
    except NoCredentialsError:
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
