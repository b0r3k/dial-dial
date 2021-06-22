from ibm_watson import AssistantV1
import json

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# ID of workspace to put the intents to
workspace_id = "41dca07d-9323-4372-8be3-ceaf4f6fad3c"

# Dialing intent
intent = "dial"
description = "User wants to call someone."
examples = [{"text": "zavolej pepovi"}, 
            {"text": "chci zavolat petrovi"}, 
            {"text": "vytoč číslo 123"}, 
            {"text": "zavolej na číslo 456"}, 
            {"text": "vytoč janu"}, 
            {"text": "spoj mě s katkou"}, 
            {"text": "chci spojit s karlem"}, 
            {"text": "chci vytočit lenku"}, 
            {"text": "chci zavolat na číslo 789"}, 
            {"text": "volej petře"}, 
            {"text": "chci volat petrovi"}]
response = assistant.create_intent(
    workspace_id=workspace_id,
    intent=intent,
    description=description,
    examples=examples)\
    .get_result()

# Greeting intent
intent = "greet"
description = "User greets."
examples = [{"text": "ahoj"}, 
            {"text": "čau"}, 
            {"text": "nazdar"}, 
            {"text": "dobrý den"}, 
            {"text": "dobré ráno"}, 
            {"text": "dobrý večer"}, 
            {"text": "dobré odpoledne"}, 
            {"text": "zdarec"}]
response = assistant.create_intent(
    workspace_id=workspace_id,
    intent=intent,
    description=description,
    examples=examples)\
    .get_result()

# Bye intent
intent = "bye"
description = "User says bye."
examples = [{"text": "nashledanou"}, 
            {"text": "hezký den"}, 
            {"text": "mějte se"}, 
            {"text": "měj se"}, 
            {"text": "zatím se měj"}, 
            {"text": "hezký zbytek dne"}]
response = assistant.create_intent(
    workspace_id=workspace_id,
    intent=intent,
    description=description,
    examples=examples)\
    .get_result()