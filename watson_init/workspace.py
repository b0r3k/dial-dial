from ibm_watson import AssistantV1
import json

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# Data
name = "dial_dial_cz"
description = "Skill for dialing in Czech language."
language = "cs"

# Create empty workspace only with data above
response = assistant.create_workspace(
    name=name,
    description=description,
    language=language,
    intents=[],
    entities=[],
    counterexamples=[],
    metadata={},
    learning_opt_out=True)\
        .get_result()

# Print response
print(json.dumps(response, indent=2, ensure_ascii=False))

# Get the workspace id for further use
workspace_id = response['workspace_id']
print('Workspace id {0}'.format(workspace_id))