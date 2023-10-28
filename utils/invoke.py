import os
import boto3

def handler(event, context):
    # Create a client for the AWS Lambda service
    lambda_client = boto3.client('lambda')

    try:
        # Invoke the 'train' function asynchronously
        response = lambda_client.invoke(
            FunctionName=os.environ['TRAINING_FUNCTION_ARN'],  # Use the environment variable
            InvocationType='Event'
        )
        print('Train function invoked:', response)
        # Return a successful response
        return {
            'statusCode': 200,
            'body': 'Train function invoked'
        }
    except Exception as e:
        print('Failed to invoke train function:', e)
        # Return a failed response
        return {
            'statusCode': 500,
            'body': 'Failed to invoke train function'
        }