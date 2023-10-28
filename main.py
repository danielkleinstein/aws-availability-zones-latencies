"""Manages cross-AZ latency testing."""

import boto3
import pickle  # nosec (remove bandit warning)
import os
import shutil
import subprocess  # nosec (remove bandit warning)
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from synchronization import write_azs_to_dynamodb, AwsAZ, AwsRegion


def get_ubuntu_ami(regional_ec2_client: boto3.client) -> str:
    """Return the latest Ubuntu 22.04 LTS AMI in the given region."""
    response = regional_ec2_client.describe_images(
        Owners=['amazon'],
        Filters=[{'Name': 'description', 'Values': ['*Ubuntu*22.04*LTS*']}]
    )

    ubuntu_images = [img for img in response['Images'] if 'UNSUPPORTED' not in img['Description']
                     and 'Pro' not in img['Description'] and 'Minimal' not in img['Description']]
    ubuntu_ami = sorted(ubuntu_images, key=lambda x: x['CreationDate'], reverse=True)[0]['ImageId']

    return ubuntu_ami


def all_regions() -> List[AwsRegion]:
    """Return a list of all AWS regions."""
    ec2_client = boto3.client('ec2')
    region_names = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    regions = []
    for region_name in region_names:
        regional_ec2_client = boto3.client('ec2', region_name=region_name)
        azs = regional_ec2_client.describe_availability_zones()['AvailabilityZones']
        az_zone_names = sorted([az['ZoneName'] for az in azs])
        az_ids = sorted([az['ZoneId'] for az in azs])
        ubuntu_ami = get_ubuntu_ami(regional_ec2_client)

        region_azs = [AwsAZ(az_zone_name, az_id, ubuntu_ami)
                      for az_zone_name, az_id in zip(az_zone_names, az_ids)]

        regions.append(AwsRegion(region_name, region_azs))

    return regions


def get_region_alias(region: str) -> str:
    """Return the Terraform alias for the given region."""
    return region.replace('-', '_')


@dataclass
class TerraformRegionData:
    """Represents Terraform data for a region."""

    REGION_NAME_REPLACE_ME: str
    REGION_ALIAS_REPLACE_ME: str
    REGION_AMI_REPLACE_ME: str
    REGION_AZ_REPLACE_ME: str


class TerraformTemplateType(Enum):
    """Represents the type of Terraform template."""

    PER_AZ = 1
    PER_REGION = 2
    GLOBAL = 3


@dataclass
class TerraformTemplate:
    """Represents Terraform template data."""

    name: str
    template_type: TerraformTemplateType

    @property
    def file_name(self) -> str:
        """Return the name of the template."""
        return f'{self.name}.tpl.tf'


def generate_terraform_file(template_str: str,
                            data: Optional[TerraformRegionData],
                            terraform_template: TerraformTemplate) -> None:
    """Generate a Terraform file from the given template and data."""
    template = template_str
    if data:
        for param in data.__dict__:
            template = template.replace(param, str(getattr(data, param)))

    if terraform_template.template_type == TerraformTemplateType.PER_AZ:
        assert data  # nosec (remove bandit warning)
        prefix = data.REGION_AZ_REPLACE_ME
    elif terraform_template.template_type == TerraformTemplateType.PER_REGION:
        assert data  # nosec (remove bandit warning)
        prefix = data.REGION_NAME_REPLACE_ME
    else:
        prefix = 'global'

    with open(f'tf/{prefix}-{terraform_template.file_name.replace(".tpl", "")}', 'w', encoding='utf-8') \
            as terraform_file:
        terraform_file.write(template)


def run_terraform() -> None:
    """Run terraform."""
    with subprocess.Popen(['terraform', 'init'],  # nosec (remove bandit warning)
                          cwd='tf', stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        _, stderr = process.communicate()
        if process.returncode != 0:
            sys.stderr.write(stderr.decode('utf-8'))
            raise ValueError('terraform init failed in tf.')

    sys.stdout.write('Terraform init successful.\n')

    with subprocess.Popen(['terraform', 'apply', '-auto-approve'],  # nosec (remove bandit warning)
                          cwd='tf', stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        _, stderr = process.communicate()
        if process.returncode != 0:
            sys.stderr.write(stderr.decode('utf-8'))
            raise ValueError('terraform apply -auto-approve failed in tf.')

    sys.stdout.write('Terraform apply successful.\n')


def destroy_terraform() -> None:
    """Run terraform."""
    with subprocess.Popen(['terraform', 'destroy', '-auto-approve'],  # nosec (remove bandit warning)
                          cwd='tf', stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        _, stderr = process.communicate()
        if process.returncode != 0:
            sys.stderr.write(stderr.decode('utf-8'))
            raise ValueError('terraform destroy -auto-approve failed in tf.')

    sys.stdout.write('Terraform destroy successful.\n')


def main() -> None:
    """Run the main logic."""
    # regions = all_regions()

    # with open('regions.pickle', 'wb') as regions_pickle_file:
    #     pickle.dump(regions, regions_pickle_file)

    with open('regions.pickle', 'rb') as regions_pickle_file:
        regions: List[AwsRegion] = pickle.load(regions_pickle_file)  # nosec (remove bandit warning)

    terraform_data: Dict[str, List[TerraformRegionData]] = {}
    for region in regions:
        terraform_data[region.name] = []
        for az in region.azs:
            terraform_data[region.name].append(TerraformRegionData(region.name,
                                                                   get_region_alias(region.name),
                                                                   az.ubuntu_ami,
                                                                   az.name))

    templates = [TerraformTemplate('ec2_instance', TerraformTemplateType.PER_AZ),
                 TerraformTemplate('ec2_instance_key_pair', TerraformTemplateType.PER_REGION),
                 TerraformTemplate('ec2_instance_role', TerraformTemplateType.GLOBAL),
                 TerraformTemplate('dynamodb_table', TerraformTemplateType.GLOBAL),
                 TerraformTemplate('output_dynamodb_table', TerraformTemplateType.GLOBAL),
                 TerraformTemplate('provider', TerraformTemplateType.PER_REGION),
                 TerraformTemplate('security_group', TerraformTemplateType.PER_REGION),
                 TerraformTemplate('sqs_queue', TerraformTemplateType.PER_AZ),
                 TerraformTemplate('sqs_control_queue', TerraformTemplateType.GLOBAL),
                 TerraformTemplate('output_ec2_instance', TerraformTemplateType.PER_AZ),
                 TerraformTemplate('output_sqs', TerraformTemplateType.PER_AZ)]

    if os.path.exists('tf') and os.path.isdir('tf'):
        destroy_terraform()

    shutil.rmtree('tf', ignore_errors=True)
    os.makedirs('tf', exist_ok=True)

    for template in templates:
        with open(f'templates/{template.file_name}', encoding='utf-8') as terraform_template_file:
            original_terraform_template = terraform_template_file.read()
            if template.template_type == TerraformTemplateType.PER_REGION:
                for region_azs in terraform_data.values():
                    generate_terraform_file(original_terraform_template, region_azs[0],
                                            template)
            elif template.template_type == TerraformTemplateType.PER_AZ:
                for region_azs in terraform_data.values():
                    for az_data in region_azs:
                        generate_terraform_file(original_terraform_template, az_data, template)
            elif template.template_type == TerraformTemplateType.GLOBAL:
                generate_terraform_file(original_terraform_template, None, template)

    run_terraform()

    for region in regions:
        write_azs_to_dynamodb(region)


if __name__ == '__main__':
    main()
