from collections import defaultdict
import json
from json.decoder import JSONDecodeError
from typing import Tuple
import entities
import editdistance
from copy import deepcopy

class NEMatcher():
    """
    Component which tries to match named entities recognized by WA to some contact list.
    """
    def __init__(self) -> None:
        self.model = None
        self.contacts_dict = None
        self.contacts_list = None


    def set_user_model(self, model) -> str:
        """
        Sets the model of instance to model given. Saves the model to "models.json" file under [id]["model"], returns the id.

        
        Parameters:
        model: ML model of given user


        Returns:
        model_id (str): id under which the model was saved
        """
        self.model = model

        # load dictionary with models from the file
        with open("models.json", encoding="utf-8", mode="r") as models_file:
            try:
                models = json.load(models_file)
            except JSONDecodeError:
                models = {}
            
        # create new id, save the model there
        models["_last_id"] = int(models["_last_id"]) + 1 if "_last_id" in models else 0
        id = str(models["_last_id"])
        if not id in models:
            models[id] = {}
        # TODO this needs to change when saving real model
        models[id]["model"] = model

        # save the dictionary back into the file
        with open("models.json", encoding="utf-8", mode="w") as models_file:
            json.dump(models, models_file)
        
        return id


    def set_contacts(self, model_id: str, contacts_dict: dict, contacts_list: list) -> None:
        """
        Sets the contacts of instance to contacts given. Saves the contacts to "models.json" file under key [model_id]["contacts"].
        The model must exist under given model_id first.

        
        Parameters:
        model_id (str): id of given user's model
        contacts_dict (dict): contacts-id matching to save to given user
        contacts_list (list): contacts list to save to given user


        Returns:
        None
        """
        self.contacts_dict = contacts_dict
        self.contacts_list = contacts_list

        # try to read the models and find given id
        read_success = False
        with open("models.json", encoding="utf-8", mode="r") as models_file:
            try:
                models = json.load(models_file)
            except JSONDecodeError as exception:
                raise Exception("Given file with models is not json-readable (maybe empty)!") from exception
            else:
                read_success = True

        # if successfull, save contacts to it and dump everything to the file
        if read_success:   
            try:
                models[model_id]["contacts_dict"] = contacts_dict
                models[model_id]["contacts_list"] = contacts_list
            except KeyError as exception:
                raise KeyError("Given model_id does not exist!") from exception
            else:
                with open("models.json", encoding="utf-8", mode="w") as models_file:
                    json.dump(models, models_file)


    def get_user_model(self, model_id: str):
        """
        Returns user's model based on the id given.

        
        Parameters:
        model_id (str): id of given user's model


        Returns:
        model: ML model of given user
        """
        with open("models.json", encoding="utf-8", mode="r") as models_file:
            try:
                models = json.load(models_file)
                # TODO this needs to change when saving real model
                model = models[model_id]["model"]
            except (JSONDecodeError, KeyError) as exception:
                raise KeyError("Given model_id does not exist!") from exception
            else:
                self.model = model
                return model


    def get_match(self, model_id: str, wa_response: dict, stt_response, wav) -> dict:
        """
        Tries to match NEs from wa_response to contacts assigned to given model_id.


        Parameters:
        model_id (str): id of given user's model.
        
        wa_response (dict): Response from the WA.

        stt_response: Speech-to-text with metadata.

        wav: Audiofile with user's input.


        Returns:
        result_ids_with_values (dict): dictionary result[id] = {"confidence": conf, "value": val}
            Confidence that given contact id was in the user's input and value corresponding to the id.
        """
        # load the model and contacts
        with open("models.json", encoding="utf-8", mode="r") as models_file:
            try:
                models = json.load(models_file)
                self.contacts_dict = models[model_id]["contacts_dict"]
                self.contacts_list = models[model_id]["contacts_list"]
                # TODO this needs to change when loading real model
                self.model = models[model_id]["model"]
            except (JSONDecodeError, KeyError) as exception:
                raise KeyError("Given model_id does not exist or it doesn't have contacts assigned!") from exception


        # get the entities from WA response, merge consecutive occurences into one
        ents = entities.parse_merge_same_entities(wa_response)["name"]
        # merge different consecutive entitites
        ents = entities.merge_different_consecutive(ents)
     
        # try to match WA returned entities to the contact list, return as entities again
        matched_to_contacts = {}
        for entity in ents:
            wa_confidence = ents[entity]["confidence"]
            # exact match
            if (matches := fuzzy_match_word_to_contacts(entity, self.contacts_dict, self.contacts_list, edit_limit=3)):
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
            elif len(parts := entity.split()) > 1:
                for part in parts:
                    if (matches := fuzzy_match_word_to_contacts(part, self.contacts_dict, self.contacts_list, edit_limit=3)):
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
        matched_to_contacts = find_contacts_around(wa_response["input"], matched_to_contacts, self.contacts_dict, self.contacts_list, edit_limit=3)
        
        # if more entities match same segment, use only the biggest match
        matched_to_contacts = entities.drop_subsets(matched_to_contacts)
        
        # drop the entities with confidence lower than 0.5
        for ent in deepcopy(matched_to_contacts):
            if matched_to_contacts[ent]["confidence"] < 0.5:
                del matched_to_contacts[ent]

        # get the new mapping
        starts, ends = entities.get_entity_starts_ends_mapping(matched_to_contacts)
        # make final result
        result_ids_with_values = defaultdict(dict)
        for start_idx in starts:
            entities_starting = starts[start_idx]
            for entity in entities_starting:
                id = self.contacts_dict[entity][0]
                result_ids_with_values[id]["value"] = entity
                # if more entities match the same location (i.e. have same start), split the confidence
                result_ids_with_values[id]["confidence"] = round((matched_to_contacts[entity]["confidence"] / len(entities_starting)), 2)

        return result_ids_with_values



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
        ent_starts, ent_ends = entities.get_entity_starts_ends_mapping(ents)
    
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