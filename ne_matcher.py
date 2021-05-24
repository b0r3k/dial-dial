import json, pickle
from json.decoder import JSONDecodeError
import entities

class NEMatcher():
    """
    Component which tries to match named entities recognized by WA to some contact list.
    """
    def __init__(self) -> None:
        self.model = None
        self.contacts = None


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


    def set_contacts(self, model_id: str, contacts: dict) -> None:
        """
        Sets the contacts of instance to contacts given. Saves the contacts to "models.json" file under key [model_id]["contacts"].
        The model must exist under given model_id first.

        
        Parameters:
        model_id (str): id of given user's model
        contacts (dict): contacts to save to given user


        Returns:
        None
        """
        self.contacts = contacts

        # try to read the models and find given id
        read_success = False
        with open("models.json", encoding="utf-8", mode="r") as models_file:
            try:
                models = json.load(models_file)
            except JSONDecodeError as exception:
                raise JSONDecodeError("Given file with models is not json-readable (maybe empty)!") from exception
            else:
                read_success = True

        print(models)
        # if successfull, save contacts to it and dump everything to the file
        if read_success:   
            try:
                models[model_id]["contacts"] = contacts
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
                model = pickle.loads(models[model_id]["model"])
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
        result_ids (dict): dictionary result[id] = confidence
            Confidence that given contact id was in the user's input.
        """
        # get the entities from WA response, merge consecutive occurences into one
        ents = entities.parse_merge_entities(wa_response)
        char_ents_mapping = entities.get_entity_char_mapping(ents)
        # if more entities match same segment, use only the biggest match
        ents = entities.drop_subsets_of_type(ents["name"], char_ents_mapping["name"])

        # load the model and contacts
        with open("models.json", encoding="utf-8", mode="r") as models_file:
            try:
                models = json.load(models_file)
                self.contacts = models[model_id]["contacts"]
                # TODO this needs to change when loading real model
                self.model = models[model_id]["model"]
            except (JSONDecodeError, KeyError) as exception:
                raise KeyError("Given model_id does not exist or it doesn't have contacts assigned!") from exception
        
        # try to match WA returned entities to the contact list
        result_ids = {}
        for entity in ents:
            wa_confidence = ents[entity]["confidence"]
            # exact match
            if entity in self.contacts:
                ids = self.contacts[entity]
                for id in ids:
                    confidence = wa_confidence * (1 / len(ids))
                    # TODO what if id is already in result? The confidence should probably be higher then - can't multiply and can't sum - maybe sum and normalize?
                    result_ids[id] = round(confidence, 2)
            
            # not matched, try split by space and match parts
            elif len(parts := entity.split()) > 1:
                num_parts_matching = sum([part in self.contacts for part in parts])
                for part in parts:
                    if part in self.contacts:
                        ids = self.contacts[part]
                        for id in ids:
                            confidence = wa_confidence * (1 / len(ids)) * (1 / num_parts_matching)
                            # TODO same as above
                            result_ids[id] = round(confidence, 2)
        
        return result_ids
