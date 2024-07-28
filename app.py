from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
import os
import requests

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
    
        # Invoke Lambda via API Gateway
        response = requests.post(
            'https://jv16aedy33.execute-api.us-east-1.amazonaws.com/Prod/upload',
            data=file_data,
            headers={
                'Content-Type': file.content_type,
                'X-File-Name': new_filename
            }
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
    # return redirect(url_for('index'))
    return render_template('error.html')

@app.route('/result')
def result():
    filename = request.args.get('filename')
    inference = request.args.get('inference', 'No inference result')
    return render_template('result.html', filename=filename, inference=inference)

if __name__ == '__main__':
    app.run(debug=True)
