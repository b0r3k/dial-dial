from os import name
from ibm_watson import AssistantV1
from ibm_watson.assistant_v1 import CreateEntity, CreateValue
import json

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# ID of workspace to put the intents to
workspace_id = "41dca07d-9323-4372-8be3-ceaf4f6fad3c"

# Get common names from prepared file
with open('czech_names/names.json', 'r') as file:
    names = json.load(file)

# Get rid of duplicates
names = set(names)

# List of CreateEntities for update_workspace method
create_entities = [CreateEntity(entity="name", description="Name of a person.", fuzzy_match=True, values=[CreateValue(name) for name in names])]

# Update the workspace
response = assistant.update_workspace(workspace_id=workspace_id, entities=create_entities)

# Print response
print(response)