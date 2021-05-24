import entities, contacts
from ne_matcher import NEMatcher

matcher = NEMatcher()

resp = entities.return_test_response()
conts_dict, conts_list = contacts.wa_contacts_to_dict_and_list(contacts.return_test_contacts())

# id = matcher.set_user_model("Here will be ML model.")
# print(f"Model saved to id {id}.")

# matcher.set_contacts(id, conts_dict, conts_list)
# print("Contacts saved to this id.")

id = "0"

matched_ids = matcher.get_match(id, resp, None, None)
print("Matched ids with confidences:")
print(matched_ids)