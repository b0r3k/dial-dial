from ibm_watson import AssistantV1
from ibm_watson.assistant_v1 import CreateEntity, CreateValue, Example
# import json

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# ID of workspace to put the intents to
workspace_id = "41dca07d-9323-4372-8be3-ceaf4f6fad3c"

# List of CreateEntities for update_workspace method
create_entities = []