import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

def should_ignore_vm(vm_name):
    # Add conditions to ignore specific VMs if needed
    return False

def get_running_vms_info(compute_client):
    running_vm_count = 0
    running_vm_names = []

    vm_list = compute_client.virtual_machines.list_all()

    for vm in vm_list:
        array = vm.id.split("/")
        resource_group = array[4]
        vm_name = array[-1]
        statuses = compute_client.virtual_machines.instance_view(resource_group, vm_name).statuses
        status = len(statuses) >= 2 and statuses[1]

        if status and status.code == 'PowerState/running' and not should_ignore_vm(vm_name):
            running_vm_count += 1
            running_vm_names.append(vm_name)

    return running_vm_count, running_vm_names

def send_slack_alert(slack_client, slack_channel, message):
    try:
        response = slack_client.chat_postMessage(
            channel=slack_channel,
            text=message
        )
        print("Slack alert sent successfully!")
    except SlackApiError as e:
        print(f"Error sending Slack alert: {e.response['error']}")

def run_azure_vm():
    # Load environment variables from .env
    load_dotenv()

    # Specify your Azure subscription ID and resource group
    azure_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    resource_group_name = os.environ.get('AZURE_RESOURCE_GROUP')

    # Specify your Slack API token and channel
    slack_token = os.environ.get('SLACK_TOKEN')
    slack_channel = os.environ.get('SLACK_CHANNEL')

    # Create a Slack WebClient
    slack_client = WebClient(token=slack_token)

    # Create an Azure Compute Management client
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, azure_subscription_id)

    running_vm_count, running_vm_names = get_running_vms_info(compute_client)

    # Check if more than 2 VMs are running
    if running_vm_count >= 1:
        # Send a Slack message with the list of running VMs
        message = f"Alert: VMs are running.\ncloud=Azure \nRunning VMs, Name: {', '.join(running_vm_names)}"
        send_slack_alert(slack_client, slack_channel, message)
    else:
        print("No action required. Number of running VMs is within the limit.cloud = Azure")

if __name__ == "__main__":
    run_azure_vm()
