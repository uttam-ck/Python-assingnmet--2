# Q4. AWS Security Best Practices
# Question:

# Your company is looking to improve its AWS security posture by ensuring the following best practices are implemented across the AWS environment:
# Ensure IAM roles have least privilege permissions. Identify any roles with overly permissive policies (e.g., AdministratorAccess).
# Check that MFA (Multi-Factor Authentication) is enabled for all IAM users and roles with sensitive access.
# Ensure that security groups are properly configured to restrict public access to sensitive services (e.g., databases, private EC2 instances).
# Identify and report any unused EC2 key pairs in the AWS account.

# Use Boto3 to:
# List all IAM roles and analyze their policies to check for overly permissive permissions.
# Verify that MFA is enabled for IAM users and roles.
# Check the inbound rules of security groups to detect potential public access (e.g., port 22, 80, 443 open to 0.0.0.0/0).
# List all EC2 key pairs and report any that are not in use.

# Outcome:
# Create a csv file for each check which lists down all critical threats which need to take action.

# Example : 
# for 1st check (eg. IAM roles have least privilege permissions)
# IAMRoleName, Policy Name (only those which have AdministratorAccess)

# for 2nd check (eg. IAM User have MFA Enabled or not)
# IAMUserName, MFAEnabled (all users MFA status either True/False)

# for 3rd check (eg. Security Group have inbound 0.0.0.0/0 allowed for ports 22,80,443)
# SGName, Port, AllowedIP 



import boto3
import csv

# Initialize AWS clients
iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')

# Function to check IAM roles for overly permissive policies
def check_iam_roles():
    print("Checking IAM roles for overly permissive policies...")
    with open('iam_roles_with_admin_access.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['IAMRoleName', 'PolicyName'])
        
        roles = iam_client.list_roles()['Roles']
        for role in roles:
            role_name = role['RoleName']
            policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
            for policy in policies:
                policy_name = policy['PolicyName']
                policy_doc = iam_client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']
                policy_version = iam_client.get_policy_version(
                    PolicyArn=policy['PolicyArn'],
                    VersionId=policy_doc['DefaultVersionId']
                )['PolicyVersion']
                if 'AdministratorAccess' in policy_name or 'FullAccess' in policy_name:
                    csvwriter.writerow([role_name, policy_name])

# Function to check if MFA is enabled for IAM users
def check_mfa_enabled():
    print("Checking MFA status for IAM users...")
    with open('iam_users_mfa_status.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['IAMUserName', 'MFAEnabled'])
        
        users = iam_client.list_users()['Users']
        for user in users:
            user_name = user['UserName']
            mfa_devices = iam_client.list_mfa_devices(UserName=user_name)['MFADevices']
            mfa_enabled = bool(mfa_devices)
            csvwriter.writerow([user_name, mfa_enabled])

# Function to check security groups for public access
def check_security_groups():
    print("Checking security groups for public access...")
    with open('security_groups_public_access.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['SGName', 'Port', 'AllowedIP'])
        
        security_groups = ec2_client.describe_security_groups()['SecurityGroups']
        for sg in security_groups:
            sg_name = sg['GroupName']
            for permission in sg['IpPermissions']:
                from_port = permission.get('FromPort', 'N/A')
                to_port = permission.get('ToPort', 'N/A')
                for ip_range in permission.get('IpRanges', []):
                    if ip_range['CidrIp'] == '0.0.0.0/0':
                        csvwriter.writerow([sg_name, f"{from_port}-{to_port}", ip_range['CidrIp']])

# Function to identify unused EC2 key pairs
def check_unused_key_pairs():
    print("Identifying unused EC2 key pairs...")
    with open('unused_ec2_key_pairs.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['KeyPairName'])
        
        key_pairs = ec2_client.describe_key_pairs()['KeyPairs']
        used_key_pairs = set()
        
        # Get all instances and collect used key pairs
        instances = ec2_client.describe_instances()['Reservations']
        for reservation in instances:
            for instance in reservation['Instances']:
                if 'KeyName' in instance:
                    used_key_pairs.add(instance['KeyName'])
        
        # Check for unused key pairs
        for key_pair in key_pairs:
            if key_pair['KeyName'] not in used_key_pairs:
                csvwriter.writerow([key_pair['KeyName']])

# Main function to run all checks
def main():
    check_iam_roles()
    check_mfa_enabled()
    check_security_groups()
    check_unused_key_pairs()
    print("All checks completed. CSV files generated.")

if __name__ == "__main__":
    main()
