import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

# Tags to ignore
ignored_tags = {'eks:cluster-name': ['microsec-dev-cluster', 'microsec-qa-cluster', 'microsec-prod-cluster', 'msec-htest']}

def should_ignore_instance(tags):
    for key, values in ignored_tags.items():
        tag_value = next((tag['Value'] for tag in tags if tag['Key'] == key), None)
        if tag_value in values:
            return True
    return False

def get_running_instances_info(region, aws_access_key_id, aws_secret_access_key):
    ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    running_count = 0
    instance_info = []

    for reservations in response['Reservations']:
        for instance in reservations['Instances']:
            if should_ignore_instance(instance.get('Tags', [])):
                continue

            running_count += 1
            instance_name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
            launch_time = instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
            instance_info.append({'Name': instance_name, 'LaunchTime': launch_time})

    return running_count, instance_info

def send_slack_alert(slack_client, slack_channel, message):
    try:
        response = slack_client.chat_postMessage(
            channel=slack_channel,
            text=message
        )
        print("Slack alert sent successfully!")
    except SlackApiError as e:
        print(f"Error sending Slack alert: {e.response['error']}")

def main(aws_access_key_id, aws_secret_access_key, slack_token, slack_channel):
    # Create a Slack WebClient
    slack_client = WebClient(token=slack_token)

    aws_regions = [
        'us-east-1', 'ap-south-1'
    ]  # Add more regions as needed

    for region in aws_regions:
        running_count, instance_info = get_running_instances_info(region, aws_access_key_id, aws_secret_access_key)

        vm_count_limit = int(os.environ.get('VM_COUNT', 0))  # Default to 0 if VM_COUNT is not set

        if running_count >= vm_count_limit:
            instance_info_str = '\n'.join([f"{info['Name']} (Launch Time: {info['LaunchTime']})" for info in instance_info])
            send_slack_alert(slack_client, slack_channel, f"Alert! There are {running_count} instances running in region={region} \ncloud=aws, ACCOUNT-ID =  681089424129(Aws-main-acc). Please check.\nInstance Information:\n{instance_info_str}")
        # else:
        #     print("No action required. Number of running VMs is within the limit.cloud = AWS, ACC-ID=620934872547 (aws-main-acc)")

def run_aws_vm_main():
    # Load environment variables from .env
    load_dotenv()

    # Specify your AWS credentials
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_account_id = os.environ.get('AWS_ACC_ID')

    # Check if credentials are set
    if aws_access_key_id is None or aws_secret_access_key is None:
        raise ValueError("AWS credentials not set in environment variables.")

    # Specify your Slack API token and channel
    slack_token = os.environ.get('SLACK_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL')

    main(aws_access_key_id, aws_secret_access_key, slack_token, slack_channel)

if __name__ == "__main__":
    run_aws_vm_main()
