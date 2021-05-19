import json
from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

api_key = 'Zgr2__7dC38Vx7vSSOQjCxUHXaTU9TmWUwFx4M381t_N'

# Authentication and assistant creation
authenticator = IAMAuthenticator(api_key)
assistant = AssistantV1(version='2021-05-19', authenticator=authenticator)
assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')

# List workspaces
response = assistant.list_workspaces().get_result()
print(json.dumps(response, indent=2))

# Print workspace with hardcoded id
response = assistant.get_workspace(
    workspace_id='0599331d-5a46-4621-9837-36079e355ece', export=True).get_result()
print(json.dumps(response, indent=2))



# Copied from example https://github.com/watson-developer-cloud/python-sdk/blob/master/examples/assistant_v1.py

# #  message
# response = assistant.message(
#     workspace_id=workspace_id,
#     input={
#         'text': 'What\'s the weather like?'
#     },
#     context={
#         'metadata': {
#             'deployment': 'myDeployment'
#         }
#     }).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_workspaces().get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_workspace(
#     workspace_id=workspace_id,
#     description='Updated test workspace.').get_result()
# print(json.dumps(response, indent=2))

# # see cleanup section below for delete_workspace example

# #########################
# # Intents
# #########################

# examples = [{"text": "good morning"}]
# response = assistant.create_intent(
#     workspace_id=workspace_id,
#     intent='test_intent',
#     description='Test intent.',
#     examples=examples).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.get_intent(
#     workspace_id=workspace_id, intent='test_intent', export=True).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_intents(
#     workspace_id=workspace_id, export=True).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_intent(
#     workspace_id=workspace_id,
#     intent='test_intent',
#     new_intent='updated_test_intent',
#     new_description='Updated test intent.').get_result()
# print(json.dumps(response, indent=2))

# # see cleanup section below for delete_intent example

# #########################
# # Examples
# #########################

# response = assistant.create_example(
#     workspace_id=workspace_id,
#     intent='updated_test_intent',
#     text='Gimme a pizza with pepperoni').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.get_example(
#     workspace_id=workspace_id,
#     intent='updated_test_intent',
#     text='Gimme a pizza with pepperoni').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_examples(
#     workspace_id=workspace_id, intent='updated_test_intent').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_example(
#     workspace_id=workspace_id,
#     intent='updated_test_intent',
#     text='Gimme a pizza with pepperoni',
#     new_text='Gimme a pizza with pepperoni').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.delete_example(
#     workspace_id=workspace_id,
#     intent='updated_test_intent',
#     text='Gimme a pizza with pepperoni').get_result()
# print(json.dumps(response, indent=2))

# #########################
# # Counter Examples
# #########################

# response = assistant.create_counterexample(
#     workspace_id=workspace_id,
#     text='I want financial advice today.').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.get_counterexample(
#     workspace_id=workspace_id,
#     text='I want financial advice today.').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_counterexamples(
#     workspace_id=workspace_id).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_counterexample(
#     workspace_id=workspace_id,
#     text='I want financial advice today.',
#     new_text='I want financial advice today.').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.delete_counterexample(
#     workspace_id=workspace_id,
#     text='I want financial advice today.').get_result()
# print(json.dumps(response, indent=2))

# #########################
# # Entities
# #########################

# values = [{"value": "juice"}]
# response = assistant.create_entity(
#     workspace_id=workspace_id,
#     entity='test_entity',
#     description='A test entity.',
#     values=values).get_result()
# print(json.dumps(response, indent=2))

# entities = [{
#     'entity':
#     'pattern_entity',
#     'values': [{
#         'value': 'value0',
#         'patterns': ['\\d{6}\\w{1}\\d{7}'],
#         'type': 'patterns'
#     }, {
#         'value':
#         'value1',
#         'patterns':
#         ['[-9][0-9][0-9][0-9][0-9]~! [1-9][1-9][1-9][1-9][1-9][1-9]'],
#         'type':
#         'patterns'
#     }, {
#         'value': 'value2',
#         'patterns': ['[a-z-9]{17}'],
#         'type': 'patterns'
#     }, {
#         'value':
#         'value3',
#         'patterns': [
#             '\\d{3}(\\ |-)\\d{3}(\\ |-)\\d{4}',
#             '\\(\\d{3}\\)(\\ |-)\\d{3}(\\ |-)\\d{4}'
#         ],
#         'type':
#         'patterns'
#     }, {
#         'value': 'value4',
#         'patterns': ['\\b\\d{5}\\b'],
#         'type': 'patterns'
#     }]
# }]
# response = assistant.create_entity(
#     workspace_id, entity=entities[0]['entity'],
#     values=entities[0]['values']).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.get_entity(
#     workspace_id=workspace_id, entity=entities[0]['entity'],
#     export=True).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_entities(workspace_id=workspace_id).get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_entity(
#     workspace_id=workspace_id,
#     entity='test_entity',
#     new_description='An updated test entity.').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.delete_entity(
#     workspace_id=workspace_id, entity='test_entity').get_result()
# print(json.dumps(response, indent=2))

# #########################
# # Synonyms
# #########################

# values = [{"value": "orange juice"}]
# assistant.create_entity(workspace_id, 'beverage', values=values).get_result()

# response = assistant.create_synonym(workspace_id, 'beverage', 'orange juice',
#                                     'oj').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.get_synonym(workspace_id, 'beverage', 'orange juice',
#                                  'oj').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_synonyms(workspace_id, 'beverage',
#                                    'orange juice').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_synonym(workspace_id, 'beverage', 'orange juice',
#                                     'oj', new_synonym='OJ').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.delete_synonym(workspace_id, 'beverage', 'orange juice',
#                                     'OJ').get_result()
# print(json.dumps(response, indent=2))

# assistant.delete_entity(workspace_id, 'beverage').get_result()

# #########################
# # Values
# #########################

# assistant.create_entity(workspace_id, 'test_entity').get_result()

# response = assistant.create_value(workspace_id, 'test_entity',
#                                   'test').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.get_value(workspace_id, 'test_entity', 'test').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.list_values(workspace_id, 'test_entity').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.update_value(workspace_id, 'test_entity', 'test',
#                                   new_value='example').get_result()
# print(json.dumps(response, indent=2))

# response = assistant.delete_value(workspace_id, 'test_entity',
#                                   'example').get_result()
# print(json.dumps(response, indent=2))

# assistant.delete_entity(workspace_id, 'test_entity').get_result()