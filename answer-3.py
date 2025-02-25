# # Q3. Write a python script which will fetch all the regions in which a customer billed for any resources. Or a customer has any resources.

import boto3

# Initialize a session using the default profile
aws_session = boto3.session.Session(profile_name="default")

# Initialize clients for EC2, S3, and RDS
ec2_client = aws_session.client(service_name="ec2")
s3_client = aws_session.client(service_name="s3")
rds_client = aws_session.client(service_name="rds")

def fetch_all_regions():

    try:
        regions_response = ec2_client.describe_regions()
        regions_list = []
        for region in regions_response['Regions']:
            regions_list.append(region['RegionName'])
        return regions_list
    except Exception as e:
        print(f"Error fetching regions: {e}")
        return []

def check_ec2_resources(region_name):
    """
    Check if there are any EC2 instances in the given region.
    """
    try:
        ec2_region_client = aws_session.client(service_name="ec2", region_name=region_name)
        ec2_response = ec2_region_client.describe_instances()
        for reservation in ec2_response['Reservations']:
            if reservation['Instances']:
                return True
    except Exception as e:
        print(f"Error checking EC2 instances in {region_name}: {e}")
    return False

def check_s3_resources():
    """
    Check if there are any S3 buckets (S3 is global, so no region-specific check).
    """
    try:
        s3_response = s3_client.list_buckets()
        if s3_response['Buckets']:
            return True
    except Exception as e:
        print(f"Error checking S3 buckets: {e}")
    return False

def check_rds_resources(region_name):
    """
    Check if there are any RDS instances in the given region.
    """
    try:
        rds_region_client = aws_session.client(service_name="rds", region_name=region_name)
        rds_response = rds_region_client.describe_db_instances()
        if rds_response['DBInstances']:
            return True
    except Exception as e:
        print(f"Error checking RDS instances in {region_name}: {e}")
    return False

def main():
    """
    Main function to fetch all regions and check for resources.
    """
    # Fetch all AWS regions
    all_regions = fetch_all_regions()
    if not all_regions:
        print("No regions found or error fetching regions.")
        return
    
    print("List of all AWS regions:")
    print(all_regions)
    
    # Check for resources in each region
    for region in all_regions:
        print(f"\nChecking resources in region: {region}")
        
        # Check for EC2 instances
        if check_ec2_resources(region):
            print(f"EC2 instances found in {region}")
        else:
            print(f"No EC2 instances found in {region}")
        
        # Check for RDS instances
        if check_rds_resources(region):
            print(f"RDS instances found in {region}")
        else:
            print(f"No RDS instances found in {region}")
        
        # Check for S3 buckets (only once since S3 is global)
        if region == "us-east-1":
            if check_s3_resources():
                print("S3 buckets found (global)")
            else:
                print("No S3 buckets found (global)")

if __name__ == "__main__":
    main()



