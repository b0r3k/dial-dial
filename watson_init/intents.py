from ibm_watson import AssistantV1
from ibm_watson.assistant_v1 import CreateIntent, Example

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# ID of workspace to put the intents to
workspace_id = "41dca07d-9323-4372-8be3-ceaf4f6fad3c"

# List of CreateIntent for update_workspace method
create_intents = []

# Dialing intent
intent = "dial"
description = "User wants to call someone."
examples = [Example(text="zavolej pepovi"), 
            Example(text="chci zavolat petrovi"), 
            Example(text="vytoč číslo 123"), 
            Example(text="zavolej na číslo 456"), 
            Example(text="vytoč janu"), 
            Example(text="spoj mě s katkou"), 
            Example(text="chci spojit s karlem"), 
            Example(text="chci vytočit lenku"), 
            Example(text="chci zavolat na číslo 789"), 
            Example(text="volej petře"), 
            Example(text="chci volat petrovi")]
create_intents.append(CreateIntent(intent=intent, description=description, examples=examples))

# Greeting intent
intent = "greet"
description = "User greets."
examples = [Example(text="ahoj"), 
            Example(text="čau"), 
            Example(text="nazdar"), 
            Example(text="dobrý den"), 
            Example(text="dobré ráno"), 
            Example(text="dobrý večer"), 
            Example(text="dobré odpoledne"), 
            Example(text="zdarec")]
create_intents.append(CreateIntent(intent=intent, description=description, examples=examples))

# Bye intent
intent = "bye"
description = "User says bye."
examples = [Example(text="nashledanou"), 
            Example(text="hezký den"), 
            Example(text="mějte se"), 
            Example(text="měj se"), 
            Example(text="zatím se měj"), 
            Example(text="hezký zbytek dne")]
create_intents.append(CreateIntent(intent=intent, description=description, examples=examples))


# Update the workspace
response = assistant.update_workspace(workspace_id=workspace_id, intents=create_intents)

# Print response
print(response)