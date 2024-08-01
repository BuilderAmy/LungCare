import sys
import boto3
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Initialize the Glue and Spark contexts
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'IMAGE_URL', 'S3_OUTPUT_DIR'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Parse the input image URL
image_url = args['IMAGE_URL']
parsed_url = urlparse(image_url)
bucket_name = parsed_url.netloc.split('.')[0]
object_key = parsed_url.path.lstrip('/')

# Define the output directory
output_dir = f"s3://{bucket_name}/{args['S3_OUTPUT_DIR']}"

# Initialize S3 client
s3 = boto3.client('s3')

# Function to process images
def process_image(image_data):
    with Image.open(BytesIO(image_data)) as img:
        # Resize image
        img = img.resize((256, 256))
        # Normalize image (if needed, here just converting to grayscale as an example)
        img = img.convert('L')  # Convert to grayscale
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

# Read the image file from S3
response = s3.get_object(Bucket=bucket_name, Key=object_key)
image_data = response['Body'].read()

# Process the image
processed_image_data = process_image(image_data)

# Generate the output key
output_key = f"{args['S3_OUTPUT_DIR']}/processed_image_{object_key.split('/')[-1]}"

# Save the processed image back to S3
s3.put_object(Bucket=bucket_name, Key=output_key, Body=processed_image_data)

# Commit the job
job.commit()
