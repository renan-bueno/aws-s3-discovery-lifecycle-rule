import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    # Obtenha a lista de todos os buckets S3
    response = s3_client.list_buckets()
    buckets = response['Buckets']

    # Itere sobre cada bucket
    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            # Tente obter a configuração de ciclo de vida do bucket
            lifecycle_config = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            rules = lifecycle_config['Rules']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                # Se não houver configuração de ciclo de vida, crie uma nova configuração
                rules = []
                rules.append({
                    'ID': 'Lifecycle-Name',
                    'Filter': {
                        'Prefix': ''
                    },
                    'Status': 'Enabled',
                    'Transitions': [
                        {
                            'Days': 30,
                            'StorageClass': 'STANDARD_IA'
                        },
                        {
                            'Days': 90,
                            'StorageClass': 'GLACIER_IR'
                        }
                    ]
                })
            else:
                # Outro erro ocorreu, trate-o conforme necessário
                raise

        # Adicione a nova regra de ciclo de vida às regras existentes


        # Aplica a configuração de ciclo de vida atualizada no bucket
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={'Rules': rules}
        )

    return {
        'statusCode': 200,
        'body': 'Regras de ciclo de vida aplicadas com sucesso nos buckets S3.'
    }
