from ibm_watson import AssistantV1
from ibm_watson.assistant_v1 import DialogNode, DialogNodeNextStep, DialogNodeOutputGeneric, DialogNodeContext, DialogNodeAction
import json

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# ID of workspace to put the intents to
workspace_id = "d8a7cb3f-9268-401d-9f5a-0355d58616fb"

dialog_nodes = []

# Node for accepting contacts, then nothing
node = {}
node["dialog_node"] = "Contacts"
node["title"] = "Přijmout kontakty"
node["conditions"] = "@contacts"
node["type"] = "standard"
context = { "contacts": "<? input.text ?>"}
node["context"] = DialogNodeContext(**context)
node = DialogNode(**node)
dialog_nodes.append(node)

# Node that detects user wants to call someone, then calls forwarding to webhook
node = {}
node["dialog_node"] = "Dial"
node["title"] = "Zavolat někomu"
node["conditions"] = "#dial"
node["type"] = "standard"
node["previous_sibling"] = "Contacts"
node["next_step"] = DialogNodeNextStep(behavior="jump_to", dialog_node="Prepare_webhook", selector="body")
node = DialogNode(**node)
dialog_nodes.append(node)

# Node that requires @name.values and $names?.length > 0, if satisfied forwards to webhook, else asks to fill
node = {}
node["dialog_node"] = "Prepare_webhook"
node["title"] = "Připravit údaje pro webhook"
node["type"] = "frame"
node["parent"] = "Dial"
node["next_step"] = DialogNodeNextStep(behavior="jump_to", dialog_node="Choose_person", selector="condition")
context = {"input": "<? input.text ?>", "entities": "<? entities.toJson() ?>"}
node["context"] = DialogNodeContext(**context)
node = DialogNode(**node)
dialog_nodes.append(node)

# Node that calls the webhook, then prompts to call a contact or asks for further disambiguation 
node = {}
node["dialog_node"] = "Choose_person"
node["title"] = "Vybrat osobu"
node["type"] = "standard"
node["parent"] = "Prepare_webhook"
node["actions"] = [DialogNodeAction(name="main_webhook", type="webhook", parameters={"contacts": "$contacts", "input": "$input", "entities": "$entities"}, result_variable="webhook_result_1")]
node["next_step"] = DialogNodeNextStep(behavior="jump_to", dialog_node="Prepare_webhook", selector="user_input")
node["conditions"] = "input != null && entities != null"
node = DialogNode(**node)
dialog_nodes.append(node)

# Update the workspace
response = assistant.update_workspace(workspace_id=workspace_id, dialog_nodes=dialog_nodes)

# Print response
print(response)