# Named Entities matching
This component tries to match NEs returned in WA response to some user contact list.

The main part of code is `ne_matcher.py`, helping functions are in `entities.py` and `contacts.py`; 
tests are in `test_*_pytest.py`.

## Part `ne_matcher.py`
The architecture of the component is not finished at all. It will probably be just a set of 
functions in the end, with no class instances with state, but left as is for now.

`set_user_model(..)`, `set_contacts(..)` and  `get_user_model(..)`, are prepared to work with ML model and contacts probably from some database, but are in a test mode, reading and writing to a json file. ML model is not used at all now.

### Function `get_match(model_id, wa_response, stt_response, wav)`
The most important part. Only `model_id` and `wa_response` are used now. 

Functions from `entities.py` are used to:

- parse the `wa_response` into dict
- merge consecutive occurances of same entity into one (useful when some entity is recognized both from name and surname), the higher confidence is kept - this maybe won't be used in the end though, because the WA will maybe return name and surname separately
- merge consecutive occurances of different entities in all combinations (useful when name and surname are recognized separately), the confidence is averaged
- drop entities with location which is a subset of another location (useful when some entity is recognized only from name and some from both name and surname)

These preprocessed entities are then matched to the dictionary of contacts. The confidence is counted as follows:

- `num_ents_matching` is number of preprocessed entities that match some contact exactly
- for each entity in `wa_response`:
    - if exact match is found, we get `ids` to which it matches
        - we save them to the result with confidence `wa_confidence * (1 / num_ents_matching) * (1 / len(ids))`
    - if exact match is not found, we try to split the entity on spaces and count `num_parts_matching` (how many parts matched something)
        - we try to match each part, if successfull, we get `ids` 
        - we save them with confidence `wa_confidence * (1 / len(ids)) * (1 / num_parts_matching) * (1 / num_ents_matching)` - this confidence may get really low, but probably not, since if the entity did not match exactly as a whole, it is not in the `num_ents_matching`

In the end we add corresponding contact names to the `ids` and return the result in dict `{id: {"confidence": confidence, "value": name}}`.