from collections import defaultdict, OrderedDict
from copy import deepcopy
from typing import Tuple



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