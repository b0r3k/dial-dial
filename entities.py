from collections import defaultdict
from copy import deepcopy

# example response to work with
def return_test_response():
    response =  {
    "intents": [
        {
        "intent": "send_money",
        "confidence": 0.8539069175720215
        }
    ],
    "entities": [
        {
        "entity": "name",
        "location": [
            10,
            15
        ],
        "value": "Petr Nosek",
        "confidence": 0.83
        },
        {
        "entity": "name",
        "location": [
            10,
            15
        ],
        "value": "Petr Svoboda",
        "confidence": 0.83
        },
        {
        "entity": "name",
        "location": [
            16,
            25
        ],
        "value": "Petr Svoboda",
        "confidence": 0.7
        }
    ],
    "input": {
        "text": "Pošli 100 Petru Svobodovi."
    },
    "output": {
        "generic": [
        {
            "response_type": "text",
            "text": "Nerozumím. Zkuste přeformulovat váš dotaz."
        }
        ],
        "text": [
        "Nerozumím. Zkuste přeformulovat váš dotaz."
        ],
        "nodes_visited": [
        "V ostatních případech"
        ],
        "log_messages": []
    },
    "context": {
        "metadata": {
        "user_id": "07ba4cb2-9e12-4edf-b2aa-e629a6b79ed4"
        },
        "conversation_id": "07ba4cb2-9e12-4edf-b2aa-e629a6b79ed4",
        "system": {
        "initialized": True,
        "dialog_stack": [
            {
            "dialog_node": "root"
            }
        ],
        "dialog_turn_counter": 1,
        "dialog_request_counter": 1,
        "_node_output_map": {
            "V ostatních případech": {
            "0": [
                0
            ]
            }
        },
        "last_branch_node": "V ostatních případech",
        "branch_exited": True,
        "branch_exited_reason": "completed"
        }
    },
    "user_id": "07ba4cb2-9e12-4edf-b2aa-e629a6b79ed4"
    }
    return response

# response = return_test_response()

def parse_merge_entities(response: dict) -> dict:
    """
    Parses entities from Watson response into more usable dict.
    If one entity is found in consecutive intervals, the intervals are merged 
    and entity is returned only once in the result.

    Parameters:
    response (dict): The response from the Watson assistant. Should contain key "entities".


    Returns:
    entities (dict): 
        Dictionary entities[entity_type][value] = {Given entity information in dict}
    """
    entities = defaultdict(dict)
    for entity in response["entities"]:
        # retrieve the values
        entity_type = entity["entity"]
        loc_start, loc_end = entity["location"][0], entity["location"][1]
        value = entity["value"]
        confidence = entity["confidence"]

        # add to the entities
        if entity_type in entities and value in entities[entity_type]:
            # this entity was already recognized somewhere, try to join location intervals
            # TODO what TODO with confidence? average? multiply?
            old_loc_start, old_loc_end = entities[entity_type][value]["location"]
            if abs(loc_start - old_loc_end) <= 1:
                # new one starts at the end of the old one, change end
                entities[entity_type][value]["location"] = old_loc_start, loc_end
            elif abs(loc_end - old_loc_start) <= 1:
                # new one ends at the beginning of the old one, change start
                entities[entity_type][value]["location"] = loc_start, old_loc_end
            else:
                # TODO two unrelated occurences of one entity in one input - what TODO?
                pass
        else:
            entities[entity_type][value] = {'value': value, 'location': (loc_start, loc_end), 'confidence': confidence}

    return entities

# try on the example response
# entities = parse_merge_entities(response)
# print(entities)



def get_entity_char_mapping(entities: dict) -> dict:
    """
    Maps entities to indices in input string.

    Parameters:
    entities (dict): The dict as return from parse_merge_entities,
    i.e. entities[entity_type][value] = {Given entity information in dict}


    Returns:
    char_ents_mapping (dict): 
        Dictionary char_ents_mapping[entity_type][char_index] = [List of entity values mapped to this index]
    """
    char_ents_mapping = defaultdict(dict)
    # go through all entities
    for entity_type in entities:
        for value in entities[entity_type]:
            # get the location
            loc_start, loc_end = entities[entity_type][value]["location"]
            # add to the char-entities mapping
            for i in range(loc_start, loc_end):
                if not i in char_ents_mapping[entity_type]:
                    char_ents_mapping[entity_type][i] = []
                char_ents_mapping[entity_type][i].append(value)

    return char_ents_mapping

# try on the example response
# char_ents_mapping = get_entity_char_mapping(entities)
# print(char_ents_mapping)



def drop_subsets_of_type(entities: dict, mapping: dict) -> dict:
    """
    Drops entities, which map to a subset of indices of another entity of the same type.
    When in the input string is "name surname", the first entity matches only the "name" and 
    the second entity matches the whole "name surname", we can drop the first one.

    Parameters:
    entities (dict): The dict of entities of given type,
    i.e. entities[value] = {Given entity information in dict}

    mapping (dict): The dict of mapping of entities of given type, 
    i.e. mapping[char_index] = [List of entity values of the type mapped to this index]


    Returns:
    entities (dict): Dict in the same form as input with subset entities dropped.
    """
    # create a copy to be able to manipulate the other dict
    entities_copy = deepcopy(entities)
    for entity, entity_dict in entities_copy.items():
        entity_start, entity_end = entity_dict["location"][0], entity_dict["location"][1]
        possible_conc = set()
        # check all indices to which this entity is mapped
        for i in range(entity_start, entity_end):
            # add entities mapped to this index as possible concurrents
            for possible in mapping[i]:
                if (possible in entities) and (not possible in possible_conc):
                    possible_conc.add(possible)
        # check all possible concurrents, delete if one is subset
        for possible in possible_conc:
            if possible in entities:
                possible_start, possible_end = entities[possible]["location"][0], entities[possible]["location"][1]
                # the possible is subset of this
                if (possible_start >= entity_start and possible_end < entity_end) or (possible_start > entity_start and possible_end <= entity_end):
                    del entities[possible]
                    continue
                # this is subset of the possible
                elif (entity_start >= possible_start and entity_end < possible_end) or (entity_start > possible_start and entity_end <= possible_end):
                    del entities[entity]

    return entities
        
# try on the example response
# entities_name = drop_subsets_of_type(entities["name"], char_ents_mapping["name"])
# print(entities_name)



# def select_biggest_matched(entities, mapping):
#     to_resolve = set()
#     for char_index in mapping:
#         matched_ents = mapping[char_index]
#         if len(matched_ents) == 1:
#             # only one entity corresponding to index -> add if not there yet
#             if not (value := matched_ents[0]) in to_resolve:
#                 to_resolve.add(value)
#         else:
#             # more entities corresponding to index -> find biggest
#             longest_match = None
#             for value in matched_ents:
#                 if value in entities:
#                     if not longest_match:
#                         longest_match = value
#                     else:
