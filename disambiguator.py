import json, pickle

class NEDisambiguator():
    """
    Component which disambiguates named entities.
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