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
id = "Contacts"
title = "Přijmout kontakty"
conditions = "@contacts"
context = { "contacts": "<? input.text ?>"}

# Node that detects user wants to call someone, then calls forwarding to webhook
id = "Dial"
title = "Zavolat někomu"
conditions = "#dial"
node_type = "standard"
previous_sibling = "Contacts"
next_step = DialogNodeNextStep(behavior="jump_to", dialog_node="Forward_webhook", selector="body")

# Node that requires @name.values and $names?.length > 0, if satisfied forwards to webhook, else asks to fill
id = "Prepare_webhook"
title = "Připravit údaje pro webhook"
node_type = "frame"
parent = "Dial"
next_step = DialogNodeNextStep(behavior="jump_to", dialog_node="Choose_person", selector="condition")
context = {"input": "<? input.text ?>", "entities": "<? entities.toJson() ?>"}

# Node that calls the webhook, then prompts to call a contact or asks for further disambiguation 
id = "Choose_person"
title = "Vybrat osobu"
node_type = "standard"
parent = "Prepare_webhook"
actions = [DialogNodeAction(name="main_webhook", type="webhook", parameters={"contacts": "$contacts", "input": "$input", "entities": "$entities"}, result_variable="webhook_result_1")]
next_step = DialogNodeNextStep(behavior="jump_to", dialog_node="Forward_webhook", selector="user_input")
conditions = "input != null && entities != null"