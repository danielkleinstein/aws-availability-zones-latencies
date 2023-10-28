"""Template script to be used as user-data for EC2 instances."""

import boto3
import json
import subprocess  # nosec (remove bandit warning)
import re
from decimal import Decimal
from typing import List, Tuple


with open('/sqs-queue', encoding='utf-8') as sqs_queue_file:
    QUEUE_URL = sqs_queue_file.read().strip()

with open('/control-sqs-queue', encoding='utf-8') as sqs_queue_file:
    CONTROL_QUEUE_URL = sqs_queue_file.read().strip()

with open('/dynamodb-write-table', encoding='utf-8') as dynamodb_write_table_file:
    WRITE_TABLE_NAME = dynamodb_write_table_file.read().strip()

with open('/dynamodb-read-table', encoding='utf-8') as dynamodb_read_table_file:
    READ_TABLE_NAME = dynamodb_read_table_file.read().strip()

with open('/region', encoding='utf-8') as region_file:
    REGION_NAME = region_file.read().strip()

with open('/az', encoding='utf-8') as region_file:
    AZ_NAME = region_file.read().strip()


def test_bandwidth(server_ip: str, port: int = 5201) -> Decimal:
    """Test network bandwidth to a host."""
    command = ['iperf3', '-c', server_ip, '-p', str(port), '-J']
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise ValueError(f'Error running iperf3: {result.stderr}')

    data = json.loads(result.stdout)
    bandwidth_bps = data['end']['sum_received']['bits_per_second']

    # Convert to Gb/s
    bandwidth_gbps = Decimal(bandwidth_bps) / Decimal(10**9)

    return bandwidth_gbps


def test_network_latency(hostname: str) -> Decimal:
    """Test network latency to a host."""
    # Run the ping command
    command = ['ping', '-c', '100', '-i', '0.1', hostname]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True)  # nosec (remove bandit warning)

    time_values = re.findall(r'time=([\d.]+)', result.stdout)
    avg_time = sum(map(Decimal, time_values)) / Decimal(len(time_values))

    return avg_time


def write_to_dynamodb(az_name: str, network_latency: Decimal, bandwidth: Decimal) -> None:
    """Write to DynamoDB."""
    dynamodb = boto3.resource('dynamodb',
                              region_name=REGION_NAME  # Arbitrary - the table is in the same region as the instance
                              )

    table = dynamodb.Table(WRITE_TABLE_NAME)

    item = {
        'availability_zone_from': AZ_NAME,
        'availability_zone_to': az_name,
        'network_latency_ms': network_latency,
        'bandwidth_gbps': bandwidth,
    }

    table.put_item(Item=item)


def read_from_dynamodb_table() -> Tuple[List[str], List[str], str]:
    """Read from the DynamoDB table."""
    dynamodb = boto3.resource('dynamodb',
                              region_name=REGION_NAME  # Arbitrary - the table is in the same region as the instance
                              )

    table = dynamodb.Table(READ_TABLE_NAME)

    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('availability_zone').eq(AZ_NAME)
    )

    azs = response.get('Items')[0].get('azs').split(',')
    pairs = [az.split(':') for az in azs]
    ips, az_names = zip(*pairs)

    next_az_queue = response.get('Items')[0].get('next_az_queue')

    return ips, az_names, next_az_queue


def trigger_next_az(next_az_queue: str) -> None:
    """Trigger the next AZ."""
    sqs = boto3.client('sqs',
                       region_name=REGION_NAME
                       )
    sqs.send_message(
        QueueUrl=next_az_queue,
        MessageBody='Go'
    )


def trigger_done() -> None:
    """Tell the control queue the region is done."""
    sqs = boto3.client('sqs',
                       region_name=REGION_NAME
                       )
    sqs.send_message(
        QueueUrl=CONTROL_QUEUE_URL,
        MessageBody=f'DONE - {REGION_NAME}'
    )


def poll_sqs_queue() -> None:
    """Poll the SQS queue for messages."""
    sqs = boto3.client('sqs',
                       region_name=REGION_NAME
                       )

    while True:
        messages = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,
        )

        if 'Messages' in messages:
            message = messages['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            # Delete message from queue
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=receipt_handle
            )

            assert message['Body'] == 'Go'  # nosec (remove bandit warning)
            break


if __name__ == '__main__':
    poll_sqs_queue()

    az_ips, az_names, next_az_queue = read_from_dynamodb_table()
    for ip, az_name in zip(az_ips, az_names):
        network_latency = test_network_latency(ip)
        bandwidth = test_bandwidth(ip)

        write_to_dynamodb(az_name, network_latency, bandwidth)

    if next_az_queue == 'DONE':
        trigger_done()
    else:
        trigger_next_az(next_az_queue)
