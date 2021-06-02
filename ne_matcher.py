from collections import defaultdict
import json
from json.decoder import JSONDecodeError
from typing import Tuple
import entities

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
        # look around those entities and try to match previous/next word to contact list
        ents = find_contacts_around(wa_response["input"], ents, self.contacts_dict, self.contacts_list, edit_limit=4)
        # get the starts and ends dictionaries
        starts, ends = entities.get_entity_starts_ends_mapping(ents)
        # merge different consecutive entitites
        ents = entities.merge_different_consecutive(ents, starts, ends)
        # get the new mapping
        starts, ends = entities.get_entity_starts_ends_mapping(ents)
        # if more entities match same segment, use only the biggest match
        ents = entities.drop_subsets(ents, starts, ends)
        
        # try to match WA returned entities to the contact list
        result_ids = {}
        num_ents_matching = sum([ent in self.contacts_dict for ent in ents])
        # avoid dividing by zero
        num_ents_matching = max(num_ents_matching, 1)
        for entity in ents:
            wa_confidence = ents[entity]["confidence"]
            # exact match
            if entity in self.contacts_dict:
                ids = self.contacts_dict[entity]
                for id in ids:
                    confidence = wa_confidence * (1 / num_ents_matching) * (1 / len(ids))
                    # TODO what if id is already in result? The confidence should probably be higher then - can't multiply and can't sum - maybe sum and normalize?
                    # at least using the higher one now
                    if id in result_ids:
                        confidence = max(confidence, result_ids[id])
                    result_ids[id] = round(confidence, 2)
            
            # not matched, try split by space and match parts
            elif len(parts := entity.split()) > 1:
                num_parts_matching = sum([part in self.contacts_dict for part in parts])
                # avoid dividing by zero
                num_parts_matching = max(num_parts_matching, 1)
                for part in parts:
                    if part in self.contacts_dict:
                        ids = self.contacts_dict[part]
                        for id in ids:
                            confidence = wa_confidence * (1 / len(ids)) * (1 / num_parts_matching) * (1 / num_ents_matching)
                            # TODO same as above
                            if id in result_ids:
                                confidence = max(confidence, result_ids[id])
                            result_ids[id] = round(confidence, 2)

        # Add corresponding contact names to ids
        result_ids_with_values = defaultdict(dict)
        for id in result_ids:
            result_ids_with_values[id]["confidence"] = result_ids[id]
            result_ids_with_values[id]["value"] = self.contacts_list[id]

        return result_ids_with_values

def find_contacts_around(input: str, entities: dict, contact_dict: dict, contact_list: list, edit_limit: int) -> dict:
    print(entities)
    

    for entity in entities:
        ent_start, ent_end = entities[entity]["location"]

    return entities

def split_input_starts_ends(input: str) -> Tuple[list, dict, dict]:
    """
        Splits the input strings on spaces, remembering the mapping from indices to words which start/end there.


        Parameters:
        input (str): Some string, usually a sentence.


        Returns:
        words (list): List of words found in the input.

        starts (dict): Dictionary starts[idx] = {Index to the list words to the word starting at idx}

        ends (dict): Dictionary ends[idx] = {Index to the list words to the word ending at idx}
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