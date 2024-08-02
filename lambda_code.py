import json
import boto3

def lambda_handler(event, context):
    # Log the entire event for debugging
    print("Event: ", json.dumps(event))
    
    # Extract the request body
    try:
        body = json.loads(event['body'])
        image_url = body['imageUrl']
        print(f"Received imageUrl: {image_url}")
        
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {str(e)} - Check if the body is a valid JSON")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"JSONDecodeError: {str(e)} - Invalid JSON"})
        }

    glue_client = boto3.client('glue')
    
    # Parse the image URL to get the bucket name and object key
    bucket_name = '2303826xrayimages'
    object_key = image_url.split('.com/')[-1]
    
    job_name = 'lungcare_glue'
    s3_output_dir = 'processed'

    # Define the arguments to pass to the Glue job
    arguments = {
        '--JOB_NAME': job_name,
        '--IMAGE_URL': image_url,
        '--S3_OUTPUT_DIR': s3_output_dir
    }

    try:
        # Start the Glue job
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments=arguments
        )
        job_run_id = response["JobRunId"]
        print(f'Glue job started successfully: {job_run_id}')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Glue job started successfully',
                'jobRunId': job_run_id
            })
        }

    except Exception as e:
        print(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error starting Glue job',
                'error': str(e)
            })
        }