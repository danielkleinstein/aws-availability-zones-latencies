import boto3
import pickle  # nosec
from typing import Dict, List

def get_all_regions() -> List[str]:
    """Retrieve all the available AWS regions."""
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    return regions


def map_az_ids_to_names_for_region(region_name: str) -> Dict[str, str]:
    """Map AZ IDs to names for a specific region."""
    ec2_client = boto3.client('ec2', region_name=region_name)
    az_response = ec2_client.describe_availability_zones()
    az_mapping = {zone['ZoneId']: zone['ZoneName'] for zone in az_response['AvailabilityZones']}
    return az_mapping


if __name__ == "__main__":
    # Check if the serialization exists
    try:
        with open('az_id_to_name.pickle', 'rb') as f:
            full_mapping = pickle.load(f)  # nosec
    except FileNotFoundError:
        full_mapping = {}
        for region in get_all_regions():
            mapping = map_az_ids_to_names_for_region(region)
            for az_id, az_name in mapping.items():
                full_mapping[az_name] = az_id

    # Serialize the mapping to a file
    with open('az_id_to_name.pickle', 'wb') as f:
        pickle.dump(full_mapping, f)

    table = """
| availability_zone_from | availability_zone_to | Latency (ms) |
|------------------------|----------------------|--------------|
| `sa-east-1a`             | `sa-east-1b`           | 2.42         |
| `me-central-1a`          | `me-central-1c`        | 1.95         |
| `ap-northeast-1a`        | `ap-northeast-1c`      | 1.87         |
| `il-central-1a`          | `il-central-1b`        | 1.70         |
| `eu-north-1b`            | `eu-north-1c`          | 1.64         |
| `ap-northeast-1a`        | `ap-northeast-1d`      | 1.54         |
| `eu-west-3a`             | `eu-west-3b`           | 1.40         |
| `sa-east-1b`             | `sa-east-1c`           | 1.39         |
| `ap-northeast-2b`        | `ap-northeast-2c`      | 1.38         |
| `eu-west-3b`             | `eu-west-3c`           | 1.36         |
| `eu-south-1b`            | `eu-south-1c`          | 1.36         |
| `ca-central-1b`          | `ca-central-1d`        | 1.25         |
| `eu-north-1a`            | `eu-north-1b`          | 1.23         |
| `me-central-1b`          | `me-central-1c`        | 1.22         |
| `eu-south-2b`            | `eu-south-2c`          | 1.22         |
| `ap-northeast-2a`        | `ap-northeast-2c`      | 1.18         |
| `eu-central-2a`          | `eu-central-2b`        | 1.18         |
| `us-east-2a`             | `us-east-2c`           | 1.13         |
| `eu-south-1a`            | `eu-south-1b`          | 1.12         |
| `eu-south-2a`            | `eu-south-2b`          | 1.09         |
| `sa-east-1a`             | `sa-east-1c`           | 1.09         |
| `eu-north-1a`            | `eu-north-1c`          | 1.05         |
| `us-west-2b`             | `us-west-2c`           | 1.05         |
| `ap-southeast-2b`        | `ap-southeast-2c`      | 1.05         |
| `ap-northeast-2b`        | `ap-northeast-2d`      | 1.04         |
| `eu-west-3a`             | `eu-west-3c`           | 1.03         |
| `eu-south-2a`            | `eu-south-2c`          | 1.02         |
| `us-west-1a`             | `us-west-1c`           | 1.02         |
| `us-east-1c`             | `us-east-1d`           | 1.01         |
| `ap-south-2a`            | `ap-south-2b`          | 1.00         |
| `me-central-1a`          | `me-central-1b`        | 1.00         |
| `eu-west-3b`             | `eu-west-3b`           | 0.99         |
| `ca-central-1a`          | `ca-central-1d`        | 0.96         |
| `ap-northeast-1c`        | `ap-northeast-1d`      | 0.94         |
| `ap-south-1b`            | `ap-south-1c`          | 0.93         |
| `ap-south-2b`            | `ap-south-2c`          | 0.93         |
| `eu-west-2b`             | `eu-west-2c`           | 0.91         |
| `eu-central-1a`          | `eu-central-1c`        | 0.91         |
| `il-central-1a`          | `il-central-1c`        | 0.90         |
| `us-east-1a`             | `us-east-1c`           | 0.89         |
| `ap-northeast-2a`        | `ap-northeast-2d`      | 0.87         |
| `ap-southeast-2a`        | `ap-southeast-2c`      | 0.87         |
| `af-south-1a`            | `af-south-1b`          | 0.87         |
| `il-central-1b`          | `il-central-1c`        | 0.87         |
| `ap-southeast-1a`        | `ap-southeast-1b`      | 0.85         |
| `ap-southeast-1b`        | `ap-southeast-1c`      | 0.81         |
| `ap-east-1b`             | `ap-east-1c`           | 0.81         |
| `us-east-1d`             | `us-east-1f`           | 0.80         |
| `eu-central-2b`          | `eu-central-2c`        | 0.79         |
| `us-east-1a`             | `us-east-1d`           | 0.79         |
| `us-east-2a`             | `us-east-2b`           | 0.79         |
| `ap-northeast-2a`        | `ap-northeast-2b`      | 0.79         |
| `ap-southeast-4a`        | `ap-southeast-4b`      | 0.77         |
| `us-east-1b`             | `us-east-1d`           | 0.77         |
| `eu-central-1a`          | `eu-central-1b`        | 0.77         |
| `ap-southeast-3a`        | `ap-southeast-3b`      | 0.76         |
| `eu-west-2a`             | `eu-west-2b`           | 0.76         |
| `us-east-1c`             | `us-east-1e`           | 0.75         |
| `ap-southeast-2a`        | `ap-southeast-2b`      | 0.75         |
| `us-east-1b`             | `us-east-1e`           | 0.74         |
| `ap-northeast-2c`        | `ap-northeast-2d`      | 0.74         |
| `eu-central-2a`          | `eu-central-2c`        | 0.74         |
| `ap-east-1a`             | `ap-east-1c`           | 0.73         |
| `eu-central-1a`          | `eu-central-1a`        | 0.73         |
| `us-east-1e`             | `us-east-1f`           | 0.72         |
| `us-west-2a`             | `us-west-2d`           | 0.72         |
| `eu-south-1a`            | `eu-south-1c`          | 0.71         |
| `eu-west-2a`             | `eu-west-2c`           | 0.68         |
| `ap-northeast-3a`        | `ap-northeast-3c`      | 0.68         |
| `af-south-1b`            | `af-south-1c`          | 0.67         |
| `ap-northeast-3a`        | `ap-northeast-3b`      | 0.66         |
| `us-west-2c`             | `us-west-2d`           | 0.66         |
| `ap-northeast-2a`        | `ap-northeast-2a`      | 0.64         |
| `us-west-2a`             | `us-west-2b`           | 0.64         |
| `eu-west-1a`             | `eu-west-1b`           | 0.62         |
| `us-west-2b`             | `us-west-2d`           | 0.62         |
| `us-east-1a`             | `us-east-1e`           | 0.61         |
| `ap-southeast-4b`        | `ap-southeast-4c`      | 0.60         |
| `ap-southeast-1a`        | `ap-southeast-1c`      | 0.59         |
| `af-south-1a`            | `af-south-1c`          | 0.59         |
| `ap-south-1a`            | `ap-south-1b`          | 0.59         |
| `eu-central-1b`          | `eu-central-1c`        | 0.59         |
| `eu-west-1a`             | `eu-west-1c`           | 0.59         |
| `ap-east-1a`             | `ap-east-1b`           | 0.58         |
| `us-east-1c`             | `us-east-1f`           | 0.57         |
| `ap-southeast-3a`        | `ap-southeast-3c`      | 0.55         |
| `me-south-1a`            | `me-south-1b`          | 0.54         |
| `ap-south-2a`            | `ap-south-2c`          | 0.52         |
| `me-south-1b`            | `me-south-1c`          | 0.51         |
| `us-east-1a`             | `us-east-1b`           | 0.50         |
| `eu-west-1b`             | `eu-west-1c`           | 0.50         |
| `us-east-1b`             | `us-east-1f`           | 0.49         |
| `us-east-2b`             | `us-east-2c`           | 0.48         |
| `ap-southeast-3b`        | `ap-southeast-3c`      | 0.47         |
| `me-south-1a`            | `me-south-1c`          | 0.46         |
| `ca-central-1a`          | `ca-central-1b`        | 0.46         |
| `us-east-1d`             | `us-east-1e`           | 0.46         |
| `us-west-2a`             | `us-west-2c`           | 0.46         |
| `us-east-1a`             | `us-east-1f`           | 0.45         |
| `us-east-1b`             | `us-east-1c`           | 0.44         |
| `ap-south-1a`            | `ap-south-1c`          | 0.43         |
| `ap-southeast-4a`        | `ap-southeast-4c`      | 0.40         |
| `ap-northeast-3b`        | `ap-northeast-3c`      | 0.39         |
| `sa-east-1c`             | `sa-east-1c`           | 0.38         |
| `us-east-1c`             | `us-east-1c`           | 0.33         |
| `sa-east-1b`             | `sa-east-1b`           | 0.33         |
| `us-west-2c`             | `us-west-2c`           | 0.32         |
| `ap-southeast-1c`        | `ap-southeast-1c`      | 0.30         |
| `ap-southeast-2b`        | `ap-southeast-2b`      | 0.30         |
| `ap-northeast-1d`        | `ap-northeast-1d`      | 0.29         |
| `eu-west-3c`             | `eu-west-3c`           | 0.28         |
| `me-south-1c`            | `me-south-1c`          | 0.27         |
| `eu-west-1a`             | `eu-west-1a`           | 0.27         |
| `eu-south-1b`            | `eu-south-1b`          | 0.26         |
| `me-south-1b`            | `me-south-1b`          | 0.25         |
| `eu-west-2b`             | `eu-west-2b`           | 0.25         |
| `eu-west-2a`             | `eu-west-2a`           | 0.25         |
| `us-west-2d`             | `us-west-2d`           | 0.25         |
| `eu-west-1b`             | `eu-west-1b`           | 0.24         |
| `ap-east-1a`             | `ap-east-1a`           | 0.24         |
| `eu-central-1c`          | `eu-central-1c`        | 0.23         |
| `eu-central-1b`          | `eu-central-1b`        | 0.23         |
| `us-east-2c`             | `us-east-2c`           | 0.22         |
| `us-east-1f`             | `us-east-1f`           | 0.22         |
| `ap-southeast-3c`        | `ap-southeast-3c`      | 0.22         |
| `us-west-1a`             | `us-west-1a`           | 0.22         |
| `eu-south-1a`            | `eu-south-1a`          | 0.21         |
| `us-east-1b`             | `us-east-1b`           | 0.21         |
| `ca-central-1a`          | `ca-central-1a`        | 0.21         |
| `af-south-1b`            | `af-south-1b`          | 0.21         |
| `ap-south-1b`            | `ap-south-1b`          | 0.21         |
| `ap-northeast-2c`        | `ap-northeast-2c`      | 0.21         |
| `eu-west-3a`             | `eu-west-3a`           | 0.20         |
| `ap-northeast-3b`        | `ap-northeast-3b`      | 0.20         |
| `ap-east-1b`             | `ap-east-1b`           | 0.20         |
| `ap-south-1a`            | `ap-south-1a`          | 0.20         |
| `ap-northeast-3a`        | `ap-northeast-3a`      | 0.19         |
| `us-east-1a`             | `us-east-1a`           | 0.19         |
| `ap-southeast-1a`        | `ap-southeast-1a`      | 0.19         |
| `sa-east-1a`             | `sa-east-1a`           | 0.19         |
| `ap-southeast-4c`        | `ap-southeast-4c`      | 0.19         |
| `af-south-1c`            | `af-south-1c`          | 0.18         |
| `ap-east-1c`             | `ap-east-1c`           | 0.18         |
| `ap-northeast-2d`        | `ap-northeast-2d`      | 0.18         |
| `eu-west-1c`             | `eu-west-1c`           | 0.18         |
| `eu-central-2c`          | `eu-central-2c`        | 0.18         |
| `eu-south-1c`            | `eu-south-1c`          | 0.18         |
| `me-central-1b`          | `me-central-1b`        | 0.18         |
| `ap-south-2c`            | `ap-south-2c`          | 0.18         |
| `ap-southeast-3a`        | `ap-southeast-3a`      | 0.18         |
| `af-south-1a`            | `af-south-1a`          | 0.18         |
| `us-east-2b`             | `us-east-2b`           | 0.18         |
| `us-west-1c`             | `us-west-1c`           | 0.18         |
| `il-central-1c`          | `il-central-1c`        | 0.18         |
| `ap-northeast-1a`        | `ap-northeast-1a`      | 0.18         |
| `eu-north-1a`            | `eu-north-1a`          | 0.18         |
| `us-east-2a`             | `us-east-2a`           | 0.17         |
| `me-south-1a`            | `me-south-1a`          | 0.17         |
| `me-central-1c`          | `me-central-1c`        | 0.17         |
| `me-central-1a`          | `me-central-1a`        | 0.17         |
| `ap-northeast-3c`        | `ap-northeast-3c`      | 0.17         |
| `ap-southeast-3b`        | `ap-southeast-3b`      | 0.17         |
| `us-east-1e`             | `us-east-1e`           | 0.17         |
| `ap-southeast-1b`        | `ap-southeast-1b`      | 0.17         |
| `ap-southeast-2c`        | `ap-southeast-2c`      | 0.17         |
| `eu-central-2b`          | `eu-central-2b`        | 0.17         |
| `us-west-2a`             | `us-west-2a`           | 0.17         |
| `us-east-1d`             | `us-east-1d`           | 0.17         |
| `ap-northeast-2b`        | `ap-northeast-2b`      | 0.16         |
| `ap-southeast-2a`        | `ap-southeast-2a`      | 0.16         |
| `ap-northeast-1c`        | `ap-northeast-1c`      | 0.16         |
| `eu-west-2c`             | `eu-west-2c`           | 0.16         |
| `ca-central-1d`          | `ca-central-1d`        | 0.16         |
| `ap-south-1c`            | `ap-south-1c`          | 0.16         |
| `eu-south-2b`            | `eu-south-2b`          | 0.16         |
| `ap-south-2b`            | `ap-south-2b`          | 0.16         |
| `us-west-2b`             | `us-west-2b`           | 0.16         |
| `il-central-1b`          | `il-central-1b`        | 0.16         |
| `ap-southeast-4a`        | `ap-southeast-4a`      | 0.16         |
| `ca-central-1b`          | `ca-central-1b`        | 0.15         |
| `eu-south-2c`            | `eu-south-2c`          | 0.15         |
| `eu-north-1b`            | `eu-north-1b`          | 0.15         |
| `il-central-1a`          | `il-central-1a`        | 0.15         |
| `eu-south-2a`            | `eu-south-2a`          | 0.15         |
| `ap-south-2a`            | `ap-south-2a`          | 0.15         |
| `eu-north-1c`            | `eu-north-1c`          | 0.14         |
| `ap-southeast-4b`        | `ap-southeast-4b`      | 0.14         |
| `eu-central-2a`          | `eu-central-2a`        | 0.13         |
    """

    for az_name, az_id in full_mapping.items():
        table = table.replace(f'`{az_name}`', f'`{az_id}`')

    print(table)
