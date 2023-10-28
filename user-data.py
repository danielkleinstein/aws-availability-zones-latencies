"""Template script to be used as user-data for EC2 instances."""

import boto3
import json
import subprocess
import re
from typing import List, Tuple


# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

with open('/sqs-queue', encoding='utf-8') as sqs_queue_file:
    QUEUE_URL = sqs_queue_file.read().strip()

with open('/dynamodb-table', encoding='utf-8') as dynamodb_table_file:
    TABLE_NAME = dynamodb_table_file.read().strip()

with open('/region', encoding='utf-8') as region_file:
    REGION_NAME = region_file.read().strip()

with open('/az', encoding='utf-8') as region_file:
    AZ_NAME = region_file.read().strip()


def write_to_dynamodb(az_name: str, network_latency: float, bandwidth: float) -> None:
    """Write to DynamoDB."""
    dynamodb = boto3.resource('dynamodb',
                              region_name=REGION_NAME  # Arbitrary - the table is in the same region as the instance
                              )

    table = dynamodb.Table(TABLE_NAME)

    item = {
        'availability_zone_from': AZ_NAME,
        'availability_zone_to': az_name,
        'network_latency_ms': network_latency,
        'bandwidth_gbps': bandwidth,
    }

    table.put_item(Item=item)


def test_bandwidth(server_ip: str, port: int = 5201) -> float:
    """Test network bandwidth to a host."""
    command = ["iperf3", "-c", server_ip, "-p", str(port), "-J"]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        raise ValueError(f"Error running iperf3: {result.stderr}")

    data = json.loads(result.stdout)
    bandwidth_bps = data["end"]["sum_received"]["bits_per_second"]

    # Convert to Gb/s
    bandwidth_gbps = bandwidth_bps / (10**9)

    return bandwidth_gbps


def test_network_latency(hostname: str) -> float:
    """Test network latency to a host."""
    # Run the ping command
    command = ["ping", "-c", "100", "-i", "0.1", hostname]
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)

    # Extract time values using regular expression
    time_values = re.findall(r"time=([\d.]+)", result.stdout)

    # Convert extracted time values to float and calculate the average
    avg_time = sum(map(float, time_values)) / len(time_values)

    return avg_time


def poll_sqs_queue() -> Tuple[List[str], List[str]]:
    """Poll the SQS queue for messages."""
    sqs = boto3.client('sqs',
                       region_name=REGION_NAME  # Arbitrary - the queue is in the same region as the instance
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

            azs = message['Body'].split(',')
            pairs = [az.split(':') for az in azs]
            ips, az_names = zip(*pairs)
            break

    return (ips, az_names)


if __name__ == '__main__':
    while True:
        az_ips, az_names = poll_sqs_queue()

        for ip, az_name in zip(az_ips, az_names):
            network_latency = test_network_latency(ip)
            bandwidth = test_bandwidth(ip)

            write_to_dynamodb(az_name, network_latency, bandwidth)