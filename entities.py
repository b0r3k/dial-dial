from collections import defaultdict

# example response to work with
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



def parse_map_entities(response: dict):
    """
    Function to parse and map entities to input string.
    If one entity is found in consecutive intervals, the intervals are merged 
    and entity is returned only once in the result.

    Parameters:
    response (dict): The response from the Watson assistant. Should contain key "entities".


    Returns:
    entities (dict): 
        Dictionary entities[entity_type][value] = {Given entity information in dict}

    char_ents_mapping (dict): 
        Dictionary char_ents_mapping[entity_type][char_index] = [List of entity values mapped to this index]
    """
    char_ents_mapping = defaultdict(dict)
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

        # add to the char-entities mapping
        for i in range(loc_start, loc_end):
            if not i in char_ents_mapping[entity_type]:
                char_ents_mapping[entity_type][i] = []
            char_ents_mapping[entity_type][i].append(value)

    return entities, char_ents_mapping

# try on the example response
entities, char_ents_mapping = parse_map_entities(response)
print(char_ents_mapping)
print(entities)
