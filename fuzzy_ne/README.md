_This documentation is in English, because it is for a component which is a part of MAMA AI library._

# Named Entities matching
This component tries to match NEs returned in WA response to some user-defined contact list.

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

These preprocessed entities are then fuzzy-matched using Levenshtein editdistance in function `fuzzy_match_word_to_contacts` to the dictionary of contacts. The function has a parameter `edit_limit` (anything further than that is considered not matching), for each element in dictionary of contacts the edit `distance` is computed. If no match is found, the original entity is splitted on spaces and partial matching is tried. The confidence is counted as follows:

- confidence returned by the function is `0.5 + 0.5*((edit_limit - distance) / edit_limit)`, so the contact with zero edit distance has confidence one
- this confidence is averaged with the WA confidence
- if two WA-returned entities match the same contact, the one with higher confidence is kept

Then the look-around is done. Basically for each word in input it is checked if before/after it is some contact matched and if yes, if this word could match the same contact (again using fuzzy-matching). If yes, the location is widened and the confidence is averaged.

Then each entity that matches only a substring of another entity is dropped (i.e. if we have some contact matching only a surname and then another matching also the word before it - presumably the name - we drop the shorter one).

Then the matches with confidence lower than `0.5` are dropped.

In the end corresponding `ids` are added to the matched contacts and if more contacts match the same segment of input, the confidence is split. The result is returned in dict `{id: {"confidence": confidence, "value": name}}`.
