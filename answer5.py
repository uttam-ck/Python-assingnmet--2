# Q5. Cost Optimization for an AWS Environment
# Your company is running multiple AWS services (EC2, RDS, Lambda, and S3) in a development account, and you have been asked to perform cost optimization by identifying unused or underutilized resources.
# Create a Python script using Boto3 to:
# Identify EC2 instances with low CPU utilization (e.g., below 10% over the past 30 days).
# List any RDS instances that are running but have been idle (i.e., no connections for over 7 days).
# Identify Lambda functions that have not been invoked in the last 30 days.
# Check for unused S3 buckets that have no objects or recent access.
# Requirements:
# Use Boto3’s CloudWatch to monitor EC2 and Lambda utilization.
# Use Boto3’s RDS and S3 APIs to retrieve the state of RDS instances and S3 buckets.
# Print a summary report listing resources that are candidates for cost-saving actions (e.g., stopping EC2 instances, deleting unused RDS databases).


import boto3
from datetime import datetime, timedelta

# Initialize AWS clients
ec2_client = boto3.client('ec2')
cloudwatch_client = boto3.client('cloudwatch')
rds_client = boto3.client('rds')
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')

# Function to check EC2 instances with low CPU utilization
def check_low_cpu_ec2_instances():
    print("Checking EC2 instances with low CPU utilization...")
    low_cpu_instances = []
    
    # Get all EC2 instances
    instances = ec2_client.describe_instances()['Reservations']
    for reservation in instances:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            
            # Get CPU utilization metrics from CloudWatch
            response = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.utcnow() - timedelta(days=30),
                EndTime=datetime.utcnow(),
                Period=86400,  # Daily granularity
                Statistics=['Average']
            )
            
            # Check if average CPU utilization is below 10%
            if response['Datapoints']:
                avg_cpu = sum(point['Average'] for point in response['Datapoints']) / len(response['Datapoints'])
                if avg_cpu < 10:
                    low_cpu_instances.append(instance_id)
    
    return low_cpu_instances

# Function to check idle RDS instances
def check_idle_rds_instances():
    print("Checking idle RDS instances...")
    idle_rds_instances = []
    
    # Get all RDS instances
    rds_instances = rds_client.describe_db_instances()['DBInstances']
    for instance in rds_instances:
        db_instance_id = instance['DBInstanceIdentifier']
        
        # Get database connections metrics from CloudWatch
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='DatabaseConnections',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            StartTime=datetime.utcnow() - timedelta(days=7),
            EndTime=datetime.utcnow(),
            Period=86400,  # Daily granularity
            Statistics=['Sum']
        )
        
        # Check if there are no connections for the last 7 days
        if not response['Datapoints'] or sum(point['Sum'] for point in response['Datapoints']) == 0:
            idle_rds_instances.append(db_instance_id)
    
    return idle_rds_instances

# Function to check unused Lambda functions
def check_unused_lambda_functions():
    print("Checking unused Lambda functions...")
    unused_lambda_functions = []
    
    # Get all Lambda functions
    functions = lambda_client.list_functions()['Functions']
    for function in functions:
        function_name = function['FunctionName']
        
        # Get invocation metrics from CloudWatch
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
            StartTime=datetime.utcnow() - timedelta(days=30),
            EndTime=datetime.utcnow(),
            Period=86400,  # Daily granularity
            Statistics=['Sum']
        )
        
        # Check if there are no invocations in the last 30 days
        if not response['Datapoints'] or sum(point['Sum'] for point in response['Datapoints']) == 0:
            unused_lambda_functions.append(function_name)
    
    return unused_lambda_functions

# Function to check unused S3 buckets
def check_unused_s3_buckets():
    print("Checking unused S3 buckets...")
    unused_s3_buckets = []
    
    # Get all S3 buckets
    buckets = s3_client.list_buckets()['Buckets']
    for bucket in buckets:
        bucket_name = bucket['Name']
        
        # Check if the bucket has no objects
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in objects:
            unused_s3_buckets.append(bucket_name)
    
    return unused_s3_buckets

# Function to print the summary report
def print_summary_report(low_cpu_instances, idle_rds_instances, unused_lambda_functions, unused_s3_buckets):
    print("\n--- Cost Optimization Summary Report ---")
    print("\n1. EC2 Instances with Low CPU Utilization (Below 10%):")
    for instance in low_cpu_instances:
        print(f"- {instance}")
    
    print("\n2. Idle RDS Instances (No Connections for 7 Days):")
    for instance in idle_rds_instances:
        print(f"- {instance}")
    
    print("\n3. Unused Lambda Functions (Not Invoked in 30 Days):")
    for function in unused_lambda_functions:
        print(f"- {function}")
    
    print("\n4. Unused S3 Buckets (No Objects):")
    for bucket in unused_s3_buckets:
        print(f"- {bucket}")

# Main function to run all checks
def main():
    low_cpu_instances = check_low_cpu_ec2_instances()
    idle_rds_instances = check_idle_rds_instances()
    unused_lambda_functions = check_unused_lambda_functions()
    unused_s3_buckets = check_unused_s3_buckets()
    
    print_summary_report(low_cpu_instances, idle_rds_instances, unused_lambda_functions, unused_s3_buckets)

if __name__ == "__main__":
    main()