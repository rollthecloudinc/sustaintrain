import os
import boto3
import json
from collections import defaultdict
import jmespath

def aggregate_by_keys(records, keys):
    """Aggregate records by a given list of keys."""
    agg_by_keys = defaultdict(list)
    for record in records:
        key_values = tuple(jmespath.search(key, record) for key in keys)
        if all(value is not None for value in key_values):
            agg_by_keys[key_values].append(record)
    return agg_by_keys

def handler(event, context):
    # Create a client for the AWS Step Functions service
    sfn_client = boto3.client('stepfunctions')

    # Get the JSON selectors from the environment variable
    aggregate_selectors = os.getenv('AGGREGATE_SELECTOR', 'data.userId').split(',')

    # Process and aggregate the events by the specified selectors
    agg_events = aggregate_by_keys(event['Records'], aggregate_selectors)

    for key_values, events in agg_events.items():
        # Start a state machine execution for each user's aggregated events
        sfn_client.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],  # Use the environment variable
            input=json.dumps(events)
        )

    return {
        'statusCode': 200,
        'body': 'Events processed and state machines started'
    }