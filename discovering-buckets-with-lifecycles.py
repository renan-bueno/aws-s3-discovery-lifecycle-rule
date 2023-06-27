import boto3

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    # List all buckets in S3
    response = s3_client.list_buckets()

    buckets = response['Buckets']
    bucket_names = [bucket['Name'] for bucket in buckets]

    # Initialize the result list
    results = []

    # Iterate over each bucket
    for bucket_name in bucket_names:
        try:
            # Get the list of objects in the bucket
            objects_response = s3_client.list_objects_v2(Bucket=bucket_name)

            # Initialize the bucket size variable
            bucket_size = 0

            # Iterate over each object and add its size to the bucket size
            for obj in objects_response["Contents"]:
                bucket_size += obj["Size"]

            # Convert the bucket size to a human-readable format
            bucket_size_readable = convert_size(bucket_size)

            # Check if the bucket has a lifecycle configuration
            response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            lifecycle_rules = response.get('Rules', [])
            if lifecycle_rules:
                lifecycle_result = "Lifecycle applied"
            else:
                lifecycle_result = "No lifecycle applied"

            # Add the bucket name, lifecycle result, and total size to the results list
            results.append([bucket_name, lifecycle_result, bucket_size_readable])
        except Exception as e:
            if 'NoSuchLifecycleConfiguration' in str(e):
                # Bucket does not have a lifecycle configuration
                results.append([bucket_name, "No lifecycle applied", bucket_size_readable])
            else:
                # An error occurred, raise the exception
                raise

    # Return the results
    return {
        'results': results
    }

def convert_size(size_bytes):
    # Convert the size from bytes to a human-readable format
    # Reference: https://stackoverflow.com/a/49361727/2515257
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names)-1:
        size_bytes /= 1024
        i += 1
    return f"{round(size_bytes, 2)} {size_names[i]}"
