import json, pickle
import entities

class NEMatcher():
    """
    Component which tries to match named entities recognized by WA to some contact list.
    """
    def __init__(self) -> None:
        self.model = None
        self.contacts = None


    def set_user_model(self, model) -> int:
        """
        Sets the model of instance to model given. Saves the model to "models.json" file under [id]["model"], returns the id.

        
        Parameters:
        model: ML model of given user


        Returns:
        model_id (int): id under which the model was saved
        """
        self.model = model
        with open("models.json", encoding="utf-8") as models_file:
            models = json.load(models_file)
            models["_last_id"] = models["_last_id"] + 1 if "_last_id" in models else 0
            id = models["_last_id"]
            if not id in models:
                models[id] = {}
            models[id]["model"] = pickle.dumps(model)
            json.dump(models, "models.json")
        return id


    def set_contacts(self, model_id: int, contacts: dict) -> None:
        """
        Sets the contacts of instance to contacts given. Saves the contacts to "models.json" file under key [model_id]["contacts"].
        The model must exist under given model_id first.

        
        Parameters:
        model_id (int): id of given user's model
        contacts (dict): contacts to save to given user


        Returns:
        None
        """
        self.contacts = contacts
        with open("models.json", encoding="utf-8") as models_file:
            models = json.load(models_file)
            models[model_id]["contacts"] = contacts
            json.dump(models, "models.json")


    def get_user_model(self, model_id):
        """
        Returns user's model based on the id given.

        
        Parameters:
        model_id (int): id of given user's model


        Returns:
        model: ML model of given user
        """
        with open("models.json", encoding="utf-8") as models_file:
            models = json.load(models_file)
            model = pickle.loads(models[model_id]["model"])
        self.model = model
        return model


    def get_match(self, model_id, wa_response, stt_response, wav):
        """
        Tries to match NEs from wa_response to contacts assigned to given model_id.


        Parameters:
        model_id (int): id of given user's model.
        
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
        with open("models.json", encoding="utf-8") as models_file:
            models = json.load(models_file)
            self.contacts = models[model_id]["contacts"]
            self.model = models[model_id]["model"]
        
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
                    result_ids[id] = round(confidence, 1)
            
            # not matched, try split by space and match parts
            elif len(parts := entity.split()) > 1:
                num_parts_matching = sum([part in self.contacts for part in parts])
                for part in parts:
                    if part in self.contacts:
                        ids = self.contacts[part]
                        for id in ids:
                            confidence = wa_confidence * (1 / len(ids)) * (1 / num_parts_matching)
                            # TODO same as above
                            result_ids[id] = round(confidence, 1)
        
        return result_ids
