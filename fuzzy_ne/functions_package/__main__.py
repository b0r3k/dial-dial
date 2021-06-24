from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import Tuple
import editdistance
import json


"""
Functions from fuzzy_ne merged into one file for easy use with IBM Cloud Funcitons
with additional changes for use with Dialog Dialer.
"""


def main(parameters: dict) -> dict:
        """
        Tries to match entities recognized by watson to contacts.

        Parameters:
        parameters (dict): json object with keys "input", "entities" and "contacts"

        Returns:
        { "entities" : matched_contacts (list) } (dict): dict with single key "entities" with value list of contacts that best match given entities
        """
        # parse the contacts
        contacts_list = json.loads(parameters["contacts"])["__contacts__"]
        contacts_dict = contacts_to_dict(contacts_list)

        # get the entities, merge consecutive occurences into one
        ents = parse_merge_same_entities(parameters["entities"])["name"]
        # merge different consecutive entitites
        ents = merge_different_consecutive(ents)
     
        # try to match WA returned entities to the contact list, return as entities again
        matched_to_contacts = {}
        for entity in ents:
            wa_confidence = ents[entity]["confidence"]
            # exact match
            matches = fuzzy_match_word_to_contacts(entity, contacts_dict, contacts_list, edit_limit=3)
            parts = entity.split()
            if matches:
                for value in matches:
                    confidence = round((matches[value] * wa_confidence), 2)
                    # TODO what if id is already in result? The confidence should probably be higher then - can't multiply and can't sum - maybe sum and normalize?
                    # at least using the higher one now
                    if value in matched_to_contacts:
                        matched_to_contacts[value]["confidence"] = max(confidence, matched_to_contacts[value]["confidence"])
                        this_start, this_end = ents[entity]["location"]
                        old_start, old_end = matched_to_contacts[value]["location"]
                        if (this_start < old_start and this_end >= old_end) or (this_start <= old_start and this_end > old_end):
                            # matches the same entity, but bigger location -> update
                            matched_to_contacts[value]["location"] = ents[entity]["location"]
                    else:
                        matched_to_contacts[value] = {}
                        matched_to_contacts[value]["confidence"] = confidence
                        matched_to_contacts[value]["value"] = value
                        matched_to_contacts[value]["location"] = ents[entity]["location"]
            
            # nothing matches, try split by space and match parts
            elif len(parts) > 1:
                for part in parts:
                    matches = fuzzy_match_word_to_contacts(part, contacts_dict, contacts_list, edit_limit=3)
                    if matches:
                        for value in matches:
                            confidence = round((matches[value] * wa_confidence), 2)
                            # TODO same as above
                            if value in matched_to_contacts:
                                matched_to_contacts[value]["confidence"] = max(confidence, matched_to_contacts[value]["confidence"])
                                ent_start, _ = ents[entity]["location"]
                                part_start = ent_start + entity.find(part)
                                part_end = part_start + len(part) + 1
                                old_start, old_end = matched_to_contacts[value]["location"]
                                if (part_start < old_start and part_end >= old_end) or (part_start <= old_start and part_end > old_end):
                                    # matches the same entity, but bigger location -> update
                                    matched_to_contacts[value]["location"] = ents[entity]["location"]
                            else:
                                matched_to_contacts[value] = {}
                                matched_to_contacts[value]["confidence"] = confidence
                                matched_to_contacts[value]["value"] = value
                                ent_start, _ = ents[entity]["location"]
                                part_start = ent_start + entity.find(part)
                                matched_to_contacts[value]["location"] = part_start, part_start + len(part) + 1 

        
        # look around matched entities and try to match previous/next word to contact list
        matched_to_contacts = find_contacts_around(parameters["input"], matched_to_contacts, contacts_dict, contacts_list, edit_limit=3)
        
        # if more entities match same segment, use only the biggest match
        matched_to_contacts = drop_subsets(matched_to_contacts)
        
        # drop the entities with confidence lower than 0.5
        for ent in deepcopy(matched_to_contacts):
            if matched_to_contacts[ent]["confidence"] < 0.5:
                del matched_to_contacts[ent]

        # get the new mapping
        starts, ends = get_entity_starts_ends_mapping(matched_to_contacts)
        # make final result
        matched_contacts = []
        for start_idx in starts:
            entities_starting = starts[start_idx]
            for entity in entities_starting:
                matched_contacts.append(entity)

        return { "entities": matched_contacts }



def find_contacts_around(input: str, ents: dict, contact_dict: dict, contact_list: list, edit_limit: int, ent_starts: dict = None, ent_ends: dict = None) -> dict:
    """
        Goes through words, if next/previous belongs to some entity, fuzzy-matches the word to each nick in contact_dict, 
        if it matches the same entity, location of that entity is widened and confidence is averaged. 


        Parameters:
        input (str): The user input.

        ents (dict): Pre-parsed entities with locations and confidences.

        contact_dict (dict): Dictionary contact_dict["Contact Nick"] = contact_id = index to the contact_list.

        contact_list (list): List of contacts, where index = ids.

        edit_limit (int): Maximum distance considered as match, corresponds confidence 0.5.

        starts (dict) (optional): Dict starts[index] = [entities_starting_here]. If not provided, it is computed.

        ends (dict) (optional): Dict ends[index] = [entities_ending_here]. If not provided, it is computed.


        Returns:
        ents (dict): Form same as original, but with fuzzy-matched words around already matched entities.
    """
    if ent_starts == None or ent_ends == None:
        # get the starts and ends mapping
        ent_starts, ent_ends = get_entity_starts_ends_mapping(ents)
    
    # split the input
    words, starts, ends = split_input_starts_ends(input)

    # for each word around entity, check if it can widen the entity
    for word, start, end in zip(words, starts, ends):
        ents_starting, ents_ending = [], []
        # check if next word is entity
        if end + 1 in ent_starts:
            ents_starting = ent_starts[end + 1]
        # check if the previous word is entity
        if start - 1 in ent_ends:
            ents_ending = ent_ends[start - 1]

        matches = []
        if ents_starting or ents_ending:
            # fuzzy match the word against each contact, return as match if under edit_limit
            matches = fuzzy_match_word_to_contacts(word, contact_dict, contact_list, edit_limit)

        # go through matches, check corresponds to the entity around
        for match in matches:
            if match in ents_starting:
                # match is same as entity in next word, widen the span of given entity
                orig_start, orig_end = ents[match]["location"]
                ents[match]["location"] = orig_start - len(word) - 1, orig_end 
                # new confidence is average
                new_confidence = round(((ents[match]["confidence"] + matches[match]) / 2), 2)
                ents[match]["confidence"] = new_confidence

            if match in ents_ending:
                # match is the same as entity in the previous word, widen the span of given entity
                orig_start, orig_end = ents[match]["location"]
                ents[match]["location"] = orig_start, orig_end + len(word) + 1
                # new confidence is average
                new_confidence = round(((ents[match]["confidence"] + matches[match]) / 2), 2)
                ents[match]["confidence"] = new_confidence
    
    return ents



def fuzzy_match_word_to_contacts(word: str, contact_dict: dict, contact_list: list, edit_limit: int) -> dict:
    """
        Tries to match each nick in contact_dict against the word, if Levenshtein distance is <= edit_limit, returns 
        as match with confidence 0.5 + 0.5*(edit_limit - distance / edit_limit). If already matched before, widens 
        the saved location and averages the confidence.


        Parameters:
        word (str): Word that should be matched.

        contact_dict (dict): Dictionary contact_dict["Contact Nick"] = contact_id = index to the contact_list.

        contact_list (list): List of contacts, where index = ids.

        edit_limit (int): Maximum distance considered as match, corresponds confidence 0.5.


        Returns:
        matches (dict): Dictionary matches["Contact Name"] = confidence it matches given word.
    """
    matched_ids = {}
    for contact_nick in contact_dict:
        distance = editdistance.eval(word, contact_nick)
        if distance <= edit_limit:
            matched = contact_dict[contact_nick]
            for id in matched:
                confidence = round((0.5 + 0.5*((edit_limit - distance) / edit_limit)), 2)
                if not id in matched_ids:
                    # add to the matched_ids with confidence the higher the smaller the distance
                    matched_ids[id] = confidence
                else:
                    # already matched, take the higher confidence
                    matched_ids[id] = max(matched_ids[id], confidence)

    # translate the ids to contact names
    matches = {}
    for id in matched_ids:
        matches[contact_list[id]] = matched_ids[id]

    return matches



def split_input_starts_ends(input: str) -> Tuple[list, dict, dict]:
    """
        Splits the input strings on spaces, remembering the mapping from indices to words which start/end there.

        Parameters:
        input (str): Some string, usually a sentence.

        Returns:
        words (list): List of words found in the input.

        starts (dict): Dictionary starts[idx] = Index to the list words to the word starting at idx

        ends (dict): Dictionary ends[idx] = Index to the list words to the word ending at idx
    """
    words, starts, ends = [], {}, {}
    word = []
    for index, char in enumerate(input):
        if char == ' ':
            words.append(''.join(word))
            word = []
            ends[index] = len(words) - 1
        elif not word:
            word.append(char)
            starts[index] = len(words)
        else:
            word.append(char)
    words.append(''.join(word))
    ends[len(input)] = len(words) - 1

    return words, starts, ends



def contacts_to_dict(contacts: list):
    """
    Parses list of contact names into dict with contact name and parts of as key and contact index as value.

    Parameters:
    contacts (list): List of contact names, e.g. ["Jana Nováková", "Jan Novák"].

    Returns:
    cont_id_dict (dict): 
        Dictionary contacts[name] = id, where contact name and each part of it is saved as key for given id,
        e.g. {"Jana": [0], "Nováková": [0], "Jan": [1], "Novák":[1]}.
    """
    cont_id_dict = defaultdict(list)
    for id, contact in enumerate(contacts):
        contact_names = [contact]
        parts = contact.split()
        if len(parts) > 1:
            contact_names += parts
        [cont_id_dict[name].append(id) for name in contact_names]
    return cont_id_dict



def parse_merge_same_entities(response_entities: list) -> dict:
    """
    Parses entities from Watson into more usable dict.
    If one entity is found in consecutive intervals, the intervals are merged 
    and entity is returned only once in the result.

    Parameters:
    response_entities (list): The entities from the Watson assistant.

    Returns:
    entities (dict): 
        Dictionary entities[entity_type][value] = {Given entity information in dict}
    """
    entities = defaultdict(dict)
    for entity in response_entities:
        # retrieve the values
        entity_type = entity["entity"]
        loc_start, loc_end = entity["location"][0], entity["location"][1]
        value = entity["value"]
        confidence = entity["confidence"]

        # add to the entities
        if entity_type in entities and value in entities[entity_type]:
            # this entity was already recognized somewhere
            # try to join location intervals
            old_loc_start, old_loc_end = entities[entity_type][value]["location"]
            if abs(loc_start - old_loc_end) <= 1:
                # new one starts at the end of the old one, change end
                entities[entity_type][value]["location"] = old_loc_start, loc_end
                # use the higher confidence
                if confidence > entities[entity_type][value]["confidence"]:
                    entities[entity_type][value]["confidence"]
            elif abs(loc_end - old_loc_start) <= 1:
                # new one ends at the beginning of the old one, change start
                entities[entity_type][value]["location"] = loc_start, old_loc_end
                # use the higher confidence
                if confidence > entities[entity_type][value]["confidence"]:
                    entities[entity_type][value]["confidence"]
            else:
                # TODO two unrelated occurences of one entity in one input - what TODO?
                pass
        else:
            entities[entity_type][value] = {'value': value, 'location': (loc_start, loc_end), 'confidence': confidence}

    return entities



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



def drop_subsets(entities: dict, starts: dict = None, ends: dict = None) -> dict:
    """
    Drops entities, which map to a subset of indices of another entity.
    When in the input string is "name surname", the first entity matches only the "name" and 
    the second entity matches the whole "name surname", we can drop the first one.

    Parameters:
    entities (dict): The dict of entities of given type,
        i.e. entities[value] = {Given entity information in dict}

    starts (dict) (optional): Dict starts[index] = [entities_starting_here]. If not provided, it is computed.

    ends (dict) (optional): Dict ends[index] = [entities_ending_here]. If not provided, it is computed.

    Returns:
    entities_copy (dict): Dict in the same form as input with subset entities dropped.
    """
    if starts == None or ends == None:
        # get the starts and ends mapping
        starts, ends = get_entity_starts_ends_mapping(entities)
    current = OrderedDict()
    entities_copy = deepcopy(entities)
    # go through input indices
    for i in range(0, max(ends) + 1):
        # check what ends on this index
        if i in ends:
            ended = ends[i]
            # sort ending entities descending based on location start so that we remove the smallest first
            loc_starts = [entities[ending]["location"][0] for ending in ended]
            loc_starts_endings = sorted(zip(loc_starts, ended), reverse=True)
            # compare location with everything currently started
            for _, ent in loc_starts_endings:
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



def merge_different_consecutive(entities: dict, starts: dict = None, ends: dict = None) -> dict:
    """
    Merges different entities with consecutive occurences. In pseudo:
    [(“Jan”, [10,13]), (“Novák”, [14,19])] is merged into [(“Jan Novák”, [10,19])]

    Parameters:
    entities (dict): The dict of entities of given type,
        i.e. entities[value] = {Given entity information in dict}

    starts (dict) (optional): Dict starts[index] = [entities_starting_here]. If not provided, it is computed.

    ends (dict) (optional): Dict ends[index] = [entities_ending_here]. If not provided, it is computed.

    Returns:
    entities_copy (dict): Dict in the same form as input with subset entities dropped.
    """
    if starts == None or ends == None:
        # get the starts and ends mapping
        starts, ends = get_entity_starts_ends_mapping(entities)
    entities_copy = deepcopy(entities)
    # go through ending indices
    for end in ends:
        # if something start on next index
        cons_start = end + 1
        if cons_start in starts:
            # find all combinations of stuff that ended and stuff that starts, but only one-word (without ' ')
            combinations = [(entities[first], entities[second]) for first in ends[end] for second in starts[cons_start] if (' ' not in first) and (' ' not in second)]
            for first, second in combinations:
                # remove the individual occurences
                if first["value"] in entities_copy:
                    del entities_copy[first["value"]]
                if second["value"] in entities_copy:
                    del entities_copy[second["value"]]
                # create the combination occurence
                new_value = first["value"] + ' ' + second["value"]
                new_location = (first["location"][0], second["location"][1])
                # compute the confidence as average
                new_confidence = round((first["confidence"] + second["confidence"]) / 2, 2)
                # if duplicate, choose higher confidence
                if new_value in entities_copy:
                    if new_confidence > entities_copy[new_value]["confidence"]:
                        entities_copy[new_value]["confidence"] = new_confidence
                # if not, save it
                else:
                    entities_copy[new_value] = {"value": new_value, "location": new_location, "confidence": new_confidence}
    
    return entities_copy