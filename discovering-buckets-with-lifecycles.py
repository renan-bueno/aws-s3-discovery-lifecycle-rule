import boto3

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    # Lista todos os buckets do S3
    response = s3_client.list_buckets()

    buckets = response['Buckets']
    bucket_names = [bucket['Name'] for bucket in buckets]

    # Verifica se cada bucket possui políticas de ciclo de vida
    buckets_with_lifecycle = []
    buckets_without_lifecycle = []
    for bucket_name in bucket_names:
        try:
            response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            lifecycle_rules = response.get('Rules', [])
            if lifecycle_rules:
                buckets_with_lifecycle.append(bucket_name)
            else:
                buckets_without_lifecycle.append(bucket_name)
        except Exception as e:
            if 'NoSuchLifecycleConfiguration' in str(e):
                buckets_without_lifecycle.append(bucket_name)
            else:
                raise

    return {
        'buckets_with_lifecycle': buckets_with_lifecycle,
        'buckets_without_lifecycle': buckets_without_lifecycle
    }