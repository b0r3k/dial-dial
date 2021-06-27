from ibm_watson import AssistantV1
from ibm_watson.assistant_v1 import DialogNode, DialogNodeNextStep, DialogNodeOutputGenericDialogNodeOutputResponseTypeText, DialogNodeContext, DialogNodeAction, DialogNodeOutputTextValuesElement, DialogNodeOutput

# Credentials need to be in a separate `ibm-credentials.env` file
# as described in https://github.com/watson-developer-cloud/python-sdk#credential-file
assistant = AssistantV1(version='2021-06-22')
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# ID of workspace to put the intents to
workspace_id = "41dca07d-9323-4372-8be3-ceaf4f6fad3c"

dialog_nodes = []

# Empty welcome node, so that there's nothing at the beginning
node = {}
node["dialog_node"] = "Welcome_empty"
node["title"] = "Úvod prázdný"
node["conditions"] = "welcome"
node["type"] = "standard"
node = DialogNode(**node)
dialog_nodes.append(node)

# Node for accepting contacts, then nothing
node = {}
node["dialog_node"] = "Contacts"
node["title"] = "Přijmout kontakty"
node["conditions"] = "@contacts"
node["type"] = "standard"
node["previous_sibling"] = "Welcome_empty"
context = { "contacts": "<? input.text ?>"}
node["context"] = DialogNodeContext(**context)
node = DialogNode(**node)
dialog_nodes.append(node)


# Node that detects user wants to call someone, then calls forwarding to webhook
node = {}
node["dialog_node"] = "Dial"
node["title"] = "Zavolat někomu"
node["conditions"] = "#dial"
node["type"] = "frame"
node["previous_sibling"] = "Contacts"
node["next_step"] = DialogNodeNextStep(behavior="jump_to", dialog_node="Prepare_webhook", selector="body")
node = DialogNode(**node)
dialog_nodes.append(node)


# Node that requires @name, if satisfied forwards to webhook, else forwards to nodes which ask to fill
node = {}
node["dialog_node"] = "Prepare_webhook"
node["title"] = "Připravit údaje pro webhook"
node["type"] = "standard"
node["parent"] = "Dial"
node["conditions"] = "1 == 1"
node["previous_sibling"] = "Slot_name"
node["next_step"] = DialogNodeNextStep(behavior="jump_to", dialog_node="Choose_person", selector="condition")
context = {"input": "<? input.text ?>", "entities": "<? entities.toJson() ?>"}
node["context"] = DialogNodeContext(**context)
node = DialogNode(**node)
dialog_nodes.append(node)


# Slot node saving into $name with children condition and response if unsatisfied
node = {}
node["dialog_node"] = "Slot_name"
node["type"] = "slot"
node["parent"] = "Dial"
node["variable"] = "$name"
node = DialogNode(**node)
dialog_nodes.append(node)

node = {}
node["dialog_node"] = "Slot_name_condition"
node["type"] = "event_handler"
node["parent"] = "Slot_name"
node["conditions"] = "@name"
context = {"name": "@name"}
node["context"] = DialogNodeContext(**context)
node["event_name"] = "input"
node = DialogNode(**node)
dialog_nodes.append(node)

node = {}
node["dialog_node"] = "Slot_name_response"
node["type"] = "event_handler"
node["parent"] = "Slot_name"
node["event_name"] = "focus"
node["previous_sibling"] = "Slot_name_condition"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="Komu chcete zavolat?"),
                        DialogNodeOutputTextValuesElement(text="První budu potřebovat vědět, komu volat."),
                        DialogNodeOutputTextValuesElement(text="S kým si přejete spojit?"),
                        DialogNodeOutputTextValuesElement(text="Kdo by měl být vytočen?")])])
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


# Response node that prompts to call
node = {}
node["dialog_node"] = "Call_person"
node["title"] = "Zavolat osobě"
node["conditions"] = "($webhook_result_1?.response?.result?.entities)?.length == 1"
node["type"] = "response_condition"
node["parent"] = "Choose_person"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="[call]\n<? context['webhook_result_1'].response.result.entities[0] ?>\nZavolám <? context['webhook_result_1'].response.result.entities[0] ?>."),
                        DialogNodeOutputTextValuesElement(text="[call]\n<? context['webhook_result_1'].response.result.entities[0] ?>\nVytáčím <? context['webhook_result_1'].response.result.entities[0] ?>."),
                        DialogNodeOutputTextValuesElement(text="[call]\n<? context['webhook_result_1'].response.result.entities[0] ?>\nVolám <? context['webhook_result_1'].response.result.entities[0] ?>."),
                        DialogNodeOutputTextValuesElement(text="[call]\n<? context['webhook_result_1'].response.result.entities[0] ?>\nZahajuji hovor s <? context['webhook_result_1'].response.result.entities[0] ?>.")])])
node = DialogNode(**node)
dialog_nodes.append(node)


# Response node stating that webhook found multiple people, asking to disambiguate
node = {}
node["dialog_node"] = "Multiple_people_found"
node["title"] = "Nalezeno více osob, upřesnit"
node["conditions"] = "($webhook_result_1?.response?.result?.entities)?.length > 1"
node["type"] = "response_condition"
node["parent"] = "Choose_person"
node["previous_sibling"] = "Call_person"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="Povedlo se mi najít následující: <? context['webhook_result_1'].response.result.entities.join(\", \") ?>. Koho z nich myslíte?"),
                        DialogNodeOutputTextValuesElement(text="Tomuto zadání odpovídá: <? context['webhook_result_1'].response.result.entities.join(\", \") ?>. Koho z nich myslíte?"),
                        DialogNodeOutputTextValuesElement(text="V kontaktech byli nalezeni následující: <? context['webhook_result_1'].response.result.entities.join(\", \") ?>. Koho z nich myslíte?")])])
node = DialogNode(**node)
dialog_nodes.append(node)


# Response node stating that webhook didn't find anything
node = {}
node["dialog_node"] = "No_person"
node["title"] = "Žádná osoba nenalezena"
node["conditions"] = "anything_else"
node["type"] = "response_condition"
node["parent"] = "Choose_person"
node["previous_sibling"] = "Multiple_people_found"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="Bohužel, nikoho takového se mi ve vašich kontaktech nepodařilo najít."),
                        DialogNodeOutputTextValuesElement(text="Všechny snahy o nalezení někoho takového selhaly."),
                        DialogNodeOutputTextValuesElement(text="Je mi líto, ale tuto osobu se ve vašich kontaktech nepovedlo najít.")])])
node = DialogNode(**node)
dialog_nodes.append(node)


# Node that detects user greets, greets back
node = {}
node["dialog_node"] = "Greet"
node["title"] = "Pozdravit"
node["conditions"] = "#greet"
node["type"] = "standard"
node["previous_sibling"] = "Dial"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="Zdravím!"),
                        DialogNodeOutputTextValuesElement(text="Dobrý den!")])])
node = DialogNode(**node)
dialog_nodes.append(node)


# Node that detects user says bye, says bye back
node = {}
node["dialog_node"] = "Bye"
node["title"] = "Rozloučit se"
node["conditions"] = "#bye"
node["type"] = "standard"
node["previous_sibling"] = "Greet"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="Mějte se!"),
                        DialogNodeOutputTextValuesElement(text="Hezký den!")])])
node = DialogNode(**node)
dialog_nodes.append(node)


# Fallback node when user's intention isn't recognized, responds that doesn't understand
node = {}
node["dialog_node"] = "Other_fallback"
node["title"] = "V ostatních případech"
node["conditions"] = "anything_else"
node["type"] = "standard"
node["previous_sibling"] = "Bye"
node["output"] = DialogNodeOutput(generic=
                    [DialogNodeOutputGenericDialogNodeOutputResponseTypeText(response_type="text", selection_policy="random", values=
                        [DialogNodeOutputTextValuesElement(text="Nerozumím. Zkuste přeformulovat váš dotaz."),
                        DialogNodeOutputTextValuesElement(text="Mohli byste se zeptat ještě jednou a trochu jinak? Nebylo porozuměno."),
                        DialogNodeOutputTextValuesElement(text="Zcela nebylo porozuměno tomu, na co se ptáte.")])])
node = DialogNode(**node)
dialog_nodes.append(node)


# Update the workspace
response = assistant.update_workspace(workspace_id=workspace_id, dialog_nodes=dialog_nodes)

# Print response
print(response)