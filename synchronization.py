"""Synchronization between tests."""

import boto3
import subprocess  # nosec (remove bandit warning)
import sys
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple


@dataclass
class AwsAZ:
    """Represents an AWS availability zone."""

    name: str
    id: str
    ubuntu_ami: str


@dataclass
class AwsRegion:
    """Represents an AWS region."""

    name: str
    azs: List[AwsAZ]

    def pairs(self) -> List[Tuple[AwsAZ, AwsAZ]]:
        """Return a list of all AZ pairs in this region."""
        return list(combinations(self.azs, 2))


def get_terraform_output(output_name: str) -> str:
    """Return the Terraform output for the given output name."""
    with subprocess.Popen(['terraform', 'output', output_name],  # nosec (remove bandit warning)
                          cwd='tf', stdout=subprocess.PIPE) as process:
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            sys.stderr.write(stderr.decode('utf-8'))
            raise ValueError(f'terraform output {output_name} failed.')

        return stdout.decode('utf-8').strip().strip('"')


def write_azs_to_dynamodb(region: AwsRegion) -> None:
    """Write AZs to DynamoDB."""
    az_pairs = region.pairs()

    # Convert pairs to dictionary of "from" AZ to "to" AZ
    az_pairs_dict: Dict[str, List[str]] = {}
    for az_pair in az_pairs:
        from_az = az_pair[0].name
        if from_az not in az_pairs_dict:
            az_pairs_dict[from_az] = [from_az]  # Make sure each AZ also has itself

        to_az = az_pair[1].name
        # This if is necessary for an edge case where an AZ is not a "from"
        # AZ for any other AZs
        if to_az not in az_pairs_dict:
            az_pairs_dict[to_az] = [to_az]

        az_pairs_dict[from_az].append(to_az)

    dynamodb = boto3.resource('dynamodb',
                              region_name='ap-south-2'  # TODO!
                              )

    table = dynamodb.Table(get_terraform_output('ec2_instance_instructions_table_name'))

    keys = list(az_pairs_dict.keys())
    for idx, az in enumerate(keys):
        if idx + 1 < len(keys):
            next_az = keys[idx + 1]
        else:
            next_az = 'DONE'

        azs = ','.join(':'.join([get_terraform_output(f'instance_ip_{to_az}'), to_az]) for to_az in az_pairs_dict[az])

        item = {
            'availability_zone': az,
            'azs': azs,
            'next_az_queue': '' if next_az == 'DONE' else get_terraform_output(f'az_sqs_queue-{next_az}')
        }

        table.put_item(Item=item)
