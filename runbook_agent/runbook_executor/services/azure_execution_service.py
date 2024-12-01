import time
from azure.identity import ClientSecretCredential
from azure.mgmt.automation import AutomationClient
from azure.mgmt.automation.models import JobCreateParameters, RunbookAssociationProperty
import uuid


class AzureRunbookExecutor:
    def __init__(self, tenant_id, client_id, client_secret, subscription_id):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id

        # Authenticate using Client Secret Credentials
        self.credentials = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        # Create the Automation client to interact with Azure Automation
        self.automation_client = AutomationClient(
            self.credentials, self.subscription_id
        )

    def get_automation_account(self, resource_group, automation_account_name):
        # List all automation accounts in the resource group
        automation_accounts = (
            self.automation_client.automation_account.list_by_resource_group(
                resource_group
            )
        )
        for account in automation_accounts:
            if account.name == automation_account_name:
                return account
        return None

    def trigger_runbook(
        self,
        resource_group,
        automation_account_name,
        runbook_name,
        parameters,
    ):
        # First, find the automation account
        automation_account = self.get_automation_account(
            resource_group, automation_account_name
        )
        if not automation_account:
            raise Exception(
                f"Automation account {automation_account_name} not found in resource group {resource_group}"
            )

        # Create RunbookAssociationProperty and pass the runbook name
        runbook_association = RunbookAssociationProperty(name=runbook_name)

        # Create JobCreateParameters and pass the correct values
        job_create_parameters = JobCreateParameters(
            runbook=runbook_association,  # Assign RunbookAssociationProperty
            parameters=parameters,  # Pass parameters dictionary
            run_on="",  # Set run_on to "" for cloud worker (or specify Hybrid Worker group name)
        )

        job_name = str(uuid.uuid4())

        # Use the correct method to start the runbook
        job = self.automation_client.job.create(
            resource_group_name=resource_group,
            automation_account_name=automation_account_name,
            job_name=job_name,
            parameters=job_create_parameters,  # Pass the parameters to the runbook
        )

        print(
            f"Runbook {runbook_name} has been triggered successfully with job ID: {job.id}"
        )
        return job_name

    def get_runbook_status(self, resource_group, automation_account_name, job_name):
        # Retrieve the status of the runbook job
        job = self.automation_client.job.get(
            resource_group_name=resource_group,
            automation_account_name=automation_account_name,
            job_name=job_name,
        )

        return job.status

    def wait_for_runbook_completion(
        self, resource_group, automation_account_name, job_id, hook_function
    ):
        # Keep checking the status of the job every 30 seconds
        while True:
            status = self.get_runbook_status(
                resource_group, automation_account_name, job_id
            )
            print(f"Job {job_id} status: {status}")

            if status in ["Completed", "Failed", "Suspended", "Stopped"]:
                response = ""
                if status == "Completed" or status == "Failed":
                    response = self.get_job_output_direct(
                        resource_group_name=resource_group,
                        automation_account_name=automation_account_name,
                        job_name=job_id,
                    )
                hook_function(status, response)
                break

            # Wait for 30 seconds before checking again
            time.sleep(30)

    def get_job_output_direct(
        self, resource_group_name, automation_account_name, job_name
    ):
        try:
            import requests

            # Get access token
            credential = self.credentials
            token = credential.get_token("https://management.azure.com/.default").token

            # Construct URL
            url = (
                f"https://management.azure.com/subscriptions/{self.subscription_id}"
                f"/resourceGroups/{resource_group_name}"
                f"/providers/Microsoft.Automation/automationAccounts/{automation_account_name}"
                f"/jobs/{job_name}/streams?api-version=2023-11-01"
            )

            # Make request
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Parse the response JSON
            response_data = response.json()

            # Initialize an empty list to store the concatenated summaries
            summaries = []

            # Iterate through the 'value' key in the response data
            for item in response_data.get("value", []):
                # Extract summary and time from each stream item
                summary = item["properties"].get("summary", "")
                time = item["properties"].get("time", "")

                # Concatenate summary and time, and add to the summaries list
                if summary:  # Only add the summary if it's not empty
                    summaries.append(f"\nTime: {time}\nSummary: {summary}\n")

            # Join all summaries into a single string with newline characters
            return "\n".join(summaries)
        except Exception as e:
            print(f"Runbook output error : {e}")
