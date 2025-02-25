
# Q1. Write a python program using boto3 to list all available types of ec2 instances in each region. Make sure the instance type won’t repeat in a region. Put it in a csv with these columns.
# region,instance_type


import boto3
import csv
from botocore.exceptions import NoCredentialsError

def list_ec2_instance_types():
    ec2_client = boto3.client("ec2")
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    with open("ec2_instance_types.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["region", "instance_type"])
        
        for region in regions:
            ec2_client = boto3.client("ec2", region_name=region)
            instance_types = set()
            
            try:
                response = ec2_client.describe_instance_type_offerings(LocationType='region', Filters=[{"Name": "location", "Values": [region]}])
                for instance in response['InstanceTypeOfferings']:
                    instance_types.add(instance['InstanceType'])
                
                for instance_type in instance_types:
                    writer.writerow([region, instance_type])
            except Exception as e:
                print(f"Error fetching instance types in {region}: {e}")

list_ec2_instance_types()