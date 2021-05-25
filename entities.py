from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import Tuple

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

def parse_merge_same_entities(response: dict) -> dict:
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
    for entity, entity_dict in entities.items():
        entity_start, entity_end = entity_dict["location"]
        possible_conc = set()
        # check all indices to which this entity is mapped
        for i in range(entity_start, entity_end):
            # add entities mapped to this index as possible concurrents
            for possible in mapping[i]:
                if (possible in entities_copy) and (not possible in possible_conc):
                    possible_conc.add(possible)
        # check all possible concurrents, delete if one is subset
        for possible in possible_conc:
            if possible in entities_copy:
                possible_start, possible_end = entities_copy[possible]["location"]
                # the possible is subset of this
                if (possible_start >= entity_start and possible_end < entity_end) or (possible_start > entity_start and possible_end <= entity_end):
                    del entities_copy[possible]
                    continue
                # this is subset of the possible
                elif (entity_start >= possible_start and entity_end < possible_end) or (entity_start > possible_start and entity_end <= possible_end):
                    del entities_copy[entity]

    return entities_copy
        
# try on the example response
# entities_name = drop_subsets_of_type(entities["name"], char_ents_mapping["name"])
# print(entities_name)



def get_entity_starts_ends_mapping(entities: dict) -> Tuple[dict, dict]:
    """
    Maps entities to their start and end indices.

    Parameters:
    entities (dict): The dict of entities of given type,
        i.e. entities[value] = {Given entity information in dict}


    Returns:
    starts (dict): Dict starts[index] = [entities_starting_here].

    ends (dict): Dict ends[index] = [entities_ending_here]
    """
    starts, ends = defaultdict(dict), defaultdict(dict)
    for entity in entities:
        entity_start, entity_end = entities[entity]["location"]
        if not entity_start in starts:
            starts[entity_start] = []
        starts[entity_start].append(entity)
        if not entity_end in ends:
            ends[entity_end] = []
        ends[entity_end].append(entity)

    return starts, ends



def drop_subsets(entities: dict, starts: dict, ends: dict) -> dict:
    """
    Drops entities, which map to a subset of indices of another entity.
    When in the input string is "name surname", the first entity matches only the "name" and 
    the second entity matches the whole "name surname", we can drop the first one.

    Parameters:
    entities (dict): The dict of entities of given type,
        i.e. entities[value] = {Given entity information in dict}

    starts (dict): Dict starts[index] = [entities_starting_here].

    ends (dict): Dict ends[index] = [entities_ending_here]


    Returns:
    entities_copy (dict): Dict in the same form as input with subset entities dropped.
    """
    current = OrderedDict()
    entities_copy = deepcopy(entities)
    # go through input indices
    for i in range(0, max(ends, key=ends.get)):
        # check what ends on this index
        if i in ends:
            ended = ends[i]
            # compare location with everything currently started
            for ent in ended:
                del current[ent]
                ent_start, ent_end = entities[ent]["location"]
                for conc in current:
                    conc_start, conc_end = entities[conc]["location"]
                    # first currently started was after this, no subset possible
                    if conc_start > ent_start:
                        break
                    # this is a subset of something, delete it
                    elif (ent_end < conc_end) or (ent_start > conc_start and ent_end <= conc_end):
                        if ent in entities_copy:
                            del entities_copy[ent]

        # check what starts on this index, add to currently started
        if i in starts:
            started = starts[i]
            for ent in started:
                current[ent] = True
        
    return entities_copy



def merge_different_consecutive(entities: dict, starts: dict, ends: dict) -> dict:
    """
    Merges different entities with consecutive occurences. In pseudo:
    [(“Jan”, [10,13]), (“Novák”, [14,19])] is merged into [(“Jan Novák”, [10,19])]

    Parameters:
    entities (dict): The dict of entities of given type,
        i.e. entities[value] = {Given entity information in dict}

    starts (dict): Dict starts[index] = [entities_starting_here].

    ends (dict): Dict ends[index] = [entities_ending_here]


    Returns:
    entities_copy (dict): Dict in the same form as input with subset entities dropped.
    """
    entities_copy = deepcopy(entities)
    # go through ending indices
    for end in ends:
        # if something start on next index
        if (cons_start := end + 1) in starts:
            # find all combinations of stuff that ended and stuff that starts, but only one-word (without ' ')
            combinations = [(entities[first], entities[second]) for first in ends[end] for second in starts[cons_start] if (' ' not in first) and (' ' not in second)]
            for first, second in combinations:
                # remove the individual occurences
                if first["value"] in entities:
                    del entities_copy[first["value"]]
                if second["value"] in entities:
                    del entities_copy[second["value"]]
                # create the combination occurence
                new_value = first["value"] + ' ' + second["value"]
                new_location = (first["location"][0], second["location"][1])
                # compute the confidence as average
                new_confidence = round((first["confidence"] + second["confidence"]) / 2, 2)
                # save it
                entities_copy[new_value] = {"value": new_value, "location": new_location, "confidence": new_confidence}
    
    return entities_copy