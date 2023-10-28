import boto3
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def handler(event, context):
    # Replace with your domain endpoint 
    host = os.environ['OPENSEARCH_DOMAIN']
    region = 'us-east-1' # For example, us-west-1

    # Set up the OpenSearch client
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    opensearch = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    # Verify that the OpenSearch client is connected
    if opensearch.ping():
        print('Connection established')
        # Return a successful response
        return {
            'statusCode': 200,
            'body': 'Connection established'
        }
    else:
        print('Connection failed')
        # Return a failed response
        return {
            'statusCode': 500,
            'body': 'Connection failed'
        }