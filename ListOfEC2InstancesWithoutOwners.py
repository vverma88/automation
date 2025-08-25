# Script iterates through the list of EC2 instances in an AWS account and creates a list of instances
# which either DO NOT have an owner tag OR have an owner tag, but the owner value is empty.

import boto3
from pprint import pprint
from botocore.exceptions import EndpointConnectionError, ClientError

session = boto3.Session(profile_name="default")

# Get list of regions where EC2 is available
regions = boto3.session.Session().get_available_regions('ec2')

# Collect all instances across regions
ec2_instance_list = []
for region in regions:
    try:
        ec2_regional_client = session.client('ec2', region_name=region)
        reservations = ec2_regional_client.describe_instances().get('Reservations', [])
        for res in reservations:
            for item in res.get('Instances', []):
                ec2_instance_list.append({
                    "ec2_instance_id": item['InstanceId'],
                    "region": region
                })
    except EndpointConnectionError:
        print(f"Skipping {region} region due to Connectivity Issue")
    except ClientError as e:
        print(f"Skipping {region} region due to Error: {e}")

# Collect instance tags
ec2_instances_with_tags_list = []
for instance in ec2_instance_list:
    client = session.client('ec2', region_name=instance['region'])
    tags = client.describe_tags(
        Filters=[{'Name': 'resource-id', 'Values': [instance['ec2_instance_id']]}]
    ).get('Tags', [])

    ec2_instances_with_tags_list.append({
        "ec2_instance_id": instance['ec2_instance_id'],
        "region": instance['region'],
        "tags": tags
    })

# Find instances without valid owner tags
ec2_instances_without_owner_tag = []

for ec2_instance in ec2_instances_with_tags_list:
    does_valid_owner_tag_exist = False
    for tag in ec2_instance['tags']:
        print(f"ec2 instance id: {ec2_instance['ec2_instance_id']} tag key: {tag['Key']} tag value: {tag['Value']}")
        if tag['Key'].lower() == 'owner' and tag['Value'].lower() != '':
            does_valid_owner_tag_exist = True

    if not does_valid_owner_tag_exist:
        ec2_instances_without_owner_tag.append(ec2_instance)

print("List of EC2 instances without owner tag: ")
pprint(ec2_instances_without_owner_tag)
