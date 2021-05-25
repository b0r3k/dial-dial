import entities, contacts
from ne_matcher import NEMatcher

matcher = NEMatcher()

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
        "value": "Petr",
        "confidence": 0.83
        },
        {
        "entity": "name",
        "location": [
            16,
            25
        ],
        "value": "Svoboda",
        "confidence": 0.7
        }
    ]
}

# ents = entities.parse_merge_same_entities(response)["name"]
# starts, ends = entities.get_entity_starts_ends_mapping(ents)
# ents = entities.merge_different_consecutive(ents, starts, ends)
# starts, ends = entities.get_entity_starts_ends_mapping(ents)
# ents = entities.drop_subsets(ents, starts, ends)
# print(ents)

# response = entities.return_test_response()
# conts_dict, conts_list = contacts.wa_contacts_to_dict_and_list(contacts.return_test_contacts())

# id = matcher.set_user_model("Here will be ML model.")
# print(f"Model saved to id {id}.")

# matcher.set_contacts(id, conts_dict, conts_list)
# print("Contacts saved to this id.")

id = "0"

matched_ids = matcher.get_match(id, response, None, None)
print("Matched ids with confidences:")
print(matched_ids)