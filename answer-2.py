# Q2. Implement transitive switching using multiple aws accounts. Let you have account A and you have to access account C via account B. Write a step by step process of creating roles and other required things. After all the process completes fetch any AWS resources list from account C.
import boto3

def list_billed_regions():
    ce_client = boto3.client("ce")
    response = ce_client.get_dimension_values(
        Dimension='REGION',
        TimePeriod={
            'Start': '2025-01-01', 
            'End': '2025-02-17'
        },
        Context='COST_AND_USAGE'
    )
    regions = [entry['Value'] for entry in response['DimensionValues']]
    print("Billed regions:", regions)
    
    list_billed_regions()