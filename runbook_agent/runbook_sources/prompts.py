from typing import List, Dict, Optional
import os
from pydantic import BaseModel
from runbook_agent.llms.open_ai import chat_completion_request_instructor
import json


class RunbookDetails(BaseModel):
    doc_id: str
    description: str


class RunbookSelectionResponse(BaseModel):
    doc_id: str
    description: str


class ActionSequenceResponse(BaseModel):
    func_name: Optional[str]
    args: Optional[Dict[str, str]]
    ambiguity: Optional[str]


class VMNamesResponse(BaseModel):
    vm_names: List[str]


class ArgumentModel(BaseModel):
    name: str
    function_to_extract: str


class RunbookAnalyserResponse(BaseModel):
    description: str
    issues_it_resolves: List[str]
    array_of_os: List[str]
    array_of_args: List[ArgumentModel]
    user_queries: List[str]


runbook_analysis_prompt = """
You are an expert runbook analyst with extensive experience in IT Service Management (ITSM) for large enterprises. Your task is to analyze the provided runbook content and extract the required information based on the following instructions:

### Instructions:
From the provided runbook content, extract and structure the following details:

1. **description**:
   - Provide a **concise description** of what the script or code does. This should be a short summary of the primary functionality or purpose of the runbook.

2. **issues_it_resolves**:
   - Describe the **issues** or **problems** the runbook is intended to resolve. This could include specific error conditions, operational failures, or any other scenarios where this runbook would be executed to fix an issue.

3. **array_of_os**:
   - Provide an **array** of the **operating systems** on which this runbook is designed to run. List each OS explicitly.

4. **array_of_args**:
   - Refer to runbook content and provide an array of **specific parameters** that **needs to be passed** by the user to execute the runbook correctly. These parameters are passed to the runbook from outside and are not defined/set in runbook itself
   - If no parameters are required return empty list

5. **arg_related_functions_to_call**:
    - List functions from the given list of function names and descriptions where both the function name and description clearly match the parameter context you need to extract.
    - Only include functions where the description or functionality is directly related to the parameter passed to the script.
    - If the relationship is not clear or the function description does not closely match the parameter purpose, do not include the function.
    - Example: If the argument is "ServerID", you should only list functions where the script uses or processes the ServerID directly. If a function getServerID() is present, return getServerID() else return empty

6. **user_queries**:
   - Provide an **array** of **possible queries** that a user might ask in incident management. These queries should be related to issues that can be **resolved** by running this runbook.
   - Consider typical queries that may arise from incidents, such as:
     - "How do I reset the password for a virtual machine?"
     - "Why is the server not responding after the update?"
     - "How do I check the status of the backup process for my VM?"
   
   Provide the top **5 most relevant** user queries that the runbook could address.
"""

fetch_VM_name_from_description_prompt = """
You are an expert system and IT analyst. Your task is to analyze the **description** provided by the user and extract any virtual machine (VM) names explicitly mentioned.

Instructions:

From the provided **general description**, extract the following details:

• **vm_names**: An array of **virtual machine names** explicitly mentioned in the description. **Only include VM names if you are 100% certain about them, and there is no ambiguity in identifying them.** If there is any uncertainty, vagueness, or potential for multiple interpretations, do **not** include them.

Please ensure the following:
- Only include **explicit VM names** that are clearly identifiable in the description.
- If any VM names are mentioned in a **generic, ambiguous, or placeholder** format (e.g., "the VM", "VM1", "a virtual machine", "VirtualMachine X"), **do not include them**.
- Do not include any references that could be dynamic placeholders or names that are unclear in the context (e.g., names given in a template-like or variable format).

For example:
- **Include**: "WebServer1", "DBServer", "AppVM"
- **Do not include**: "the VM", "VM X", "virtual machine", "VM instance", "VM with 4 cores"

Note:
- Only include **actual VM names** as mentioned in the description, and ensure they are distinct and unambiguous. If the description references dynamic or undefined placeholders (like variables or unspecific VM terms), **omit them**.
"""

runbook_selection_prompt = """
[Identity]:
    You are a virtual assistant designed to analyze incident descriptions and suggest the most relevant runbook(s) from a set of predefined candidates. Your task is to analyze the incident description, match it with the appropriate runbooks based on their descriptions, and return the most suitable `doc_id` of the runbook to be executed. If no runbook is relevant, return an empty `doc_id`.

[Instructions]:

**Incident Description Analysis:**
- When an incident is described, compare the incident's nature and symptoms against the descriptions of the top 5 runbooks provided.
- Evaluate which runbook best aligns with the issue described in the incident.
- Consider the following factors when making your decision:
  - Keywords and phrases in the incident description
  - The specificity and relevance of each runbook’s description
  - Any technical indicators or terminology used in both the incident and runbook descriptions
  - If multiple runbooks are relevant but one stands out as being more directly related to the issue, choose the most appropriate one.
  
**Runbook Matching Logic:**
- If a match is found, return the `doc_id` of the runbook to be executed.
- If no runbook matches the incident, return `doc_id = ""`.

**Runbook Descriptions:**
- Each runbook comes with a `doc_id` and a `description`.
- The `description` should help you understand the context and the actions the runbook addresses.
  
**Examples of Matching:**
- If the incident description is related to a VM performance issue, look for a runbook that addresses VM performance or system diagnostics.
- If the incident is related to disk space issues, match it with a runbook that provides steps for resolving disk space problems.

**Return Format:**
- Return the `doc_id` of the most appropriate runbook based on the analysis.
- If no runbook fits, return an empty `doc_id` as `""`.
- Return a brief description of what the runbook does as `description`

[Runbook Format]:
- A list of the top 5 runbooks is provided in the following format:

1. `doc_id`: <Runbook Identifier>
   `description`: <Description of what the runbook does>
"""

base_action_sequence_prompt = """
You are an expert system designed to analyze provided incident descriptions and map them to a predefined set of functions with strict adherence to accuracy. Your task is to determine which functions should be called based on the input description, infer the exact arguments from the description to pass, and handle scenarios where multiple actions are requested.

### Instructions:

1. **Input Description Analysis**:
   - Analyze the provided incident description to identify all distinct actions being requested, in the order they appear.
   - Extract only the information explicitly mentioned in the description or clearly inferred without ambiguity.
   - Include any specific entity or identifier mentioned in the description in your analysis.
   - If any issue is being reported, actions should be taken immediately, and the function must be mapped accordingly.

2. **Entity-Specific Actions**:
   - Ensure actions are linked to the specific entity mentioned in the description by the user.
   - If the entity is ambiguous or missing, include this in the ambiguity note.

3. **Function Mapping**:
   - For each described action, map it to a function from the predefined list.
   - Extract or infer arguments directly from the description where possible.
   - If a described action does not provide all required arguments explicitly or contains ambiguity, do not output the function call. Include an ambiguity note in the output.
   - Required arguments (marked as `true`) must either be explicitly provided in the description or inferred without ambiguity. Optional arguments can be omitted.

4. **Output Requirements**:
   - For each identified action that can be fully matched:
     - Output the function name and the exact arguments to pass, clearly derived from the description.
     - Use the following output format for each action:
       ```
       functionName=<function_name>
       argument1=value1
       argument2=value2
       ```
   - If multiple actions are requested, list them sequentially in the output, maintaining their order in the description.
   - For any ambiguities, include them at the beginning of the output using the format:
       ```
       Ambiguity: [Description of the issue]
       ```

5. **Predefined Function List**:
   {function_list_json}

6. **Ambiguity Handling**:
   - If any described action does not clearly specify all required arguments or is ambiguous, include an ambiguity note in the output.
   - If an action does not match any function from the predefined list, include it under ambiguity notes stating that no matching function was found.

7. **Example**:
   - **Input Description**: "Monitor server resources and validate user input."
   - **Function List**:
     - **Function Name**: monitorResources
       - Description: Monitors the resource usage of a specified server.
       - Required Arguments: `serverName`
     - **Function Name**: validateInput
       - Description: Validates the specified input.
       - Required Arguments: `inputData`
   - **Output**:
     ```
     Ambiguity: Missing serverName for monitoring resources.
     Ambiguity: Missing inputData for validating user input.
     ```

8. **Notes**:
   - Ensure the output contains all identified actions requested in the description, in sequence.
   - Maintain the order of actions and ambiguities as they appear in the input description.
   - Avoid making assumptions or using default values for missing arguments.
   - Only output actions with all required arguments provided.
   - Clearly format ambiguities as specified.
"""


# Define the list of functions as dictionaries
function_list = [
    {
        "FunctionName": "SchdeuleTaskForExecution",
        "Description": "Schedules the mentioned task to be executed at a specified time. Task : {description}",
        "Arguments": [
            {
                "Name": "start_time",
                "Required": True,
                "Description": "The time at which the task should be executed for the first time. Must be in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SS±HH:MM'). Example: '2024-12-22T08:00:00+05:30' for 22nd December 2024 at 8:00 AM IST.",
            },
            {
                "Name": "expiry_time",
                "Required": False,
                "Description": "Specifies time on which the schdeule will stop executing the task. Must be in ISO 8601 format (e.g., 'YYYY-MM-DDTHH:MM:SS±HH:MM'). Example: '2024-12-22T08:00:00+05:30' for 22nd December 2024 at 8:00 AM IST.",
            },
            {
                "Name": "interval",
                "Required": True,
                "Description": "Specifies the numeric time interval at which the task should be executed. Will be used along with frequency argument",
            },
            {
                "Name": "frequency",
                "Required": True,
                "Description": "Determines how often the task should run. Accepted values are: OneTime (Executes only once at the specified time), Day (Runs daily at the specified interval), Hour (Runs hourly), Week (Runs weekly), Month (Runs monthly). Is dependent on interval value.",
            },
            {
                "Name": "time_zone",
                "Required": True,
                "Description": "The time zone for the schedule in the **IANA format**",
            },
        ],
        "Examples": [
            {
                "Description": "Schedule task X on 8 December 2024 at 8 pm IST",
                "Argument inference": "start_time - '2024-12-8T20:00:00+05:30', interval-1(Since task is to be executed once), frequency-OneTime, time_zone - Asia/Kolkata (IANA for IST)",
            },
            {
                "Description": "Schedule task X everyday from 23 December 2024 to 26 December 2024 at 5 pm IST",
                "Argument inference": "start_time - 23 December 2024, 5 PM IST (schedule start time); expiry_time - 26 December 2024, 5 PM IST (schedule expiry); interval - 1 (task to be executed once per day); frequency - Daily; time_zone - Asia/Kolkata (IANA for IST)",
            },
        ],
    },
    {
        "FunctionName": "TriggerTaskImmediately",
        "Description": "Triggers mentioned task or takes action on the described issue. Task - {description}",
        "Arguments": [],
        "Examples": [
            {
                "Description": "High CPU usage on XXX",
            }
        ],
    },
]

function_list_json = json.dumps(function_list, indent=4)
action_sequence_prompt = base_action_sequence_prompt.replace(
    "{function_list_json}", function_list_json
)


list_of_function = {
    "get_subscription_id()": "This will return the Azure subscription ID associated with the account.",
    "get_resource_group_name()": "Returns the name of the Azure resource group where resources are located.",
    "get_tenant_id()": "Returns the Azure Active Directory tenant ID associated with the subscription.",
    "get_VM_names()": "Returns the names of vm names",
    "get_aws_access_key()": "Return access key for AWS",
    "get_aws_secret_key()": "Return secret for AWS",
    "get_aws_region()": "Returns aws region",
}


def get_subscription_id():
    return "8a73585c-429c-4438-900a-3202dc668d02"


def get_resource_group_name():
    return "nva_auto_resolve_demo_rg"


def get_tenant_id():
    return os.getenv("TENANT_ID")


def get_aws_access_key():
    return os.getenv("AWS_ACCESS_KEY_ID")


def get_aws_secret_key():
    return os.getenv("AWS_SECRET_ACCESS_KEY")


def get_aws_region():
    return os.getenv("AWS_REGION")


def get_VM_names(description: str) -> VMNamesResponse:
    response = chat_completion_request_instructor(
        get_vm_names_from_description_prompt(description=description),
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=4000,
        response_model=VMNamesResponse,
    )
    return response


function_map = {
    "get_subscription_id()": get_subscription_id,
    "get_resource_group_name()": get_resource_group_name,
    "get_tenant_id()": get_tenant_id,
    "get_vm_names()": get_VM_names,
    "get_aws_access_key()": get_aws_access_key,
    "get_aws_secret_key()": get_aws_secret_key,
    "get_aws_region()": get_aws_region,
}


def runbook_selection(description: str, runbooks: RunbookDetails) -> str:
    messages = [
        {
            "role": "system",
            "content": runbook_selection_prompt,
        },
        {
            "role": "user",
            "content": f"Runbooks: {runbooks},\n Incident description: {description}",
        },
    ]
    return messages


def get_runbook_analysis_message(runbook: str, list_of_functions: List[str]) -> str:
    messages = [
        {
            "role": "system",
            "content": runbook_analysis_prompt,
        },
        {
            "role": "user",
            "content": f"Runbook content: {runbook},\n list of functions with description: {list_of_functions}",
        },
    ]
    return messages


def get_vm_names_from_description_prompt(description: str) -> str:
    messages = [
        {
            "role": "system",
            "content": fetch_VM_name_from_description_prompt,
        },
        {
            "role": "user",
            "content": f"Description: {description}",
        },
    ]
    return messages


def get_action_sequence_prompt(
    ticket_description: str,
    selected_runbook_description: str,
    user_entity_information: str,
) -> str:
    messages = [
        {
            "role": "system",
            "content": action_sequence_prompt.replace(
                "{description}", selected_runbook_description
            ),
        },
        {
            "role": "user",
            "content": f"Incident description: {ticket_description}. {user_entity_information}",
        },
    ]
    return messages


def select_runbook_for_execution(
    description: str, runbooks: RunbookDetails
) -> RunbookSelectionResponse:
    response = chat_completion_request_instructor(
        runbook_selection(runbooks=runbooks, description=description),
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=4000,
        response_model=RunbookSelectionResponse,
    )
    return response


def action_sequences(
    ticket_description: str,
    selected_runbook_description: str,
    user_entity_information: str,
) -> RunbookSelectionResponse:
    response = chat_completion_request_instructor(
        get_action_sequence_prompt(
            ticket_description=ticket_description,
            selected_runbook_description=selected_runbook_description,
            user_entity_information=user_entity_information,
        ),
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=4000,
        response_model=ActionSequenceResponse,
    )
    return response
