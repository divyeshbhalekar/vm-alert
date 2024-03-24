import boto3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
# import logging
# logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv

def get_running_instances_info(region, aws_access_key_id, aws_secret_access_key):
    ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    running_count = sum([len(reservations['Instances']) for reservations in response['Reservations']])
  
    # Extract instance names and launch times
    instance_info = []
    for reservations in response['Reservations']:
        for instance in reservations['Instances']:
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
        'us-east-1', 'us-east-2' ,'us-west-1', 'us-west-2',
        'ap-south-1', 'ap-southeast-1','ap-southeast-2',  'ap-northeast-3', 'ap-northeast-2',
        'ap-northeast-1', 'ca-central-1', 'eu-north-1', 'eu-west-3',
        'eu-west-2', 'eu-west-1', 'eu-central-1', 'sa-east-1'
    ]  # Add more regions as needed

    for region in aws_regions:
        running_count, instance_info = get_running_instances_info(region, aws_access_key_id, aws_secret_access_key)

        vm_count_limit = int(os.environ.get('VM_COUNT', 0))  # Default to 0 if VM_COUNT is not set

        if running_count >= vm_count_limit:
            instance_info_str = '\n'.join([f"{info['Name']} (Launch Time: {info['LaunchTime']})" for info in instance_info])
            send_slack_alert(slack_client, slack_channel, f"Alert! There are {running_count} instances running in region={region} \ncloud=aws, ACCOUNT-ID = 399612969457 (Aws-test-acc). Please check.\nInstance Information:\n{instance_info_str}")
        else:
            print("No action required. Number of running VMs is within the limit.cloud = AWS, ACC-ID=399612969457 (aws-test-acc)")


def run_aws_vm_test():
    # Load environment variables from .env
    load_dotenv()

    # Specify your AWS credentials
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID_TEST_ACC')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY_TEST_ACC')

    # Check if credentials are set
    if aws_access_key_id is None or aws_secret_access_key is None:
        raise ValueError("AWS credentials not set in environment variables.")

    # Specify your Slack API token and channel
    slack_token = os.environ.get('SLACK_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL')

    main(aws_access_key_id, aws_secret_access_key, slack_token, slack_channel)

if __name__ == "__main__":
    run_aws_vm_test()
