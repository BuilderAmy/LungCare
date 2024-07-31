import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

# Initialize the Glue and Spark contexts
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_INPUT_BUCKET', 'S3_INPUT_KEY', 'S3_OUTPUT_BUCKET', 'S3_OUTPUT_KEY'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define input and output paths
input_path = f"s3://{args['S3_INPUT_BUCKET']}/{args['S3_INPUT_KEY']}"
output_path = f"s3://{args['S3_OUTPUT_BUCKET']}/{args['S3_OUTPUT_KEY']}"

# Read the image file from S3 as binary file
binary_df = spark.read.format("binaryFile").load(input_path)

# Perform some simple transformation
# Here we are just logging the file details
file_info = binary_df.select("path", "length")
file_info.show(truncate=False)

# Save the transformation result back to S3 as CSV
file_info.write.mode("overwrite").csv(output_path)

# Commit the job
job.commit()
