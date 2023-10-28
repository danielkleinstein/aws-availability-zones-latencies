"""Template script to be used as user-data for EC2 instances."""

import boto3
from typing import List


sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

with open('/sqs-queue', encoding='utf-8') as sqs_queue_file:
    QUEUE_URL = sqs_queue_file.read().strip()

with open('/dynamodb-table', encoding='utf-8') as dynamodb_table_file:
    TABLE_NAME = dynamodb_table_file.read().strip()

# def process_az(az):
#     response = table.get_item(
#         Key={
#             'AZ': az
#         }
#     )

#     ip = response['Item']['IP']


def poll_sqs_queue() -> List[str]:
    """Poll the SQS queue for messages."""
    sqs = boto3.client('sqs')

    while True:
        messages = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )

        if 'Messages' in messages:
            message = messages['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Delete message from queue
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=receipt_handle
            )

            azs = message['Body'].split(',')

    return azs


if __name__ == '__main__':
    azs = poll_sqs_queue()

    # Write azs to "test.txt"
    with open('/test.txt', 'w', encoding='utf-8') as test_file:
        test_file.write('\n'.join(azs))