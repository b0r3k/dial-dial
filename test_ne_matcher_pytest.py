import ne_matcher
import json, pytest

def test_set_user_model_empty():
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        pass
    nematch = ne_matcher.NEMatcher()

    assert nematch.set_user_model("test0") == "0"

def test_set_user_model_one():
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {"_last_id": 0, "0": {"model": "test0"}}
        json.dump(models, models_file)
    nematch = ne_matcher.NEMatcher()

    assert nematch.set_user_model("test1") == "1"


def test_set_contacts_empty():
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        pass
    nematch = ne_matcher.NEMatcher()
    
    with pytest.raises(Exception):
        nematch.set_contacts(0, None, None)

def test_set_contacts_id_not():
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {}
        json.dump(models, models_file)
    nematch = ne_matcher.NEMatcher()
    
    with pytest.raises(KeyError):
        nematch.set_contacts(0, None, None)

def test_set_contacts_valid():
    id = "0"
    conts_dict, conts_list = {"test": [0]}, ["test"]
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {"_last_id": 0, id: {"model": "test0"}}
        json.dump(models, models_file)
    nematch = ne_matcher.NEMatcher()
    nematch.set_contacts(id, conts_dict, conts_list)
    with open("models.json", encoding="utf-8", mode="r") as models_file:
        models = json.load(models_file)
        saved_dict, saved_list = models[id]["contacts_dict"], models[id]["contacts_list"]

    assert conts_dict == saved_dict and conts_list == saved_list


def test_get_user_model_empty():
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        pass
    nematch = ne_matcher.NEMatcher()
    
    with pytest.raises(KeyError):
        nematch.get_user_model("0")

def test_get_user_model_id_not():
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {}
        json.dump(models, models_file)
    nematch = ne_matcher.NEMatcher()
    
    with pytest.raises(KeyError):
        nematch.get_user_model("0")

def test_get_user_model_valid():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {"_last_id": 1, id: {"model": model}, "1": {"model": "test1"}}
        json.dump(models, models_file)
    nematch = ne_matcher.NEMatcher()

    assert nematch.get_user_model(id) == model


def test_get_match_base():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {  "_last_id": 0, 
        id: { "model": model, 
            "contacts_dict": {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}, 
            "contacts_list":  ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'] }    }
        json.dump(models, models_file)
    response = {"entities": [ { "entity": "name", "location": [ 10, 15 ], "value": "Petr Nosek", "confidence": 0.83 } ], "input": "" }
    nematch = ne_matcher.NEMatcher()

    assert nematch.get_match(id, response, None, None) == {4: {"confidence": 0.83, "value": "Petr Nosek"}}

def test_get_match_simple_ambg():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {  "_last_id": 0, 
        id: { "model": model, 
            "contacts_dict": {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}, 
            "contacts_list":  ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'] }    }
        json.dump(models, models_file)
    response = {"entities": [ { "entity": "name", "location": [ 10, 15 ], "value": "Petr", "confidence": 0.83 } ], "input": "" }
    nematch = ne_matcher.NEMatcher()

    # two matches -> confidence is split in halves
    assert nematch.get_match(id, response, None, None) == {4: {"confidence": 0.41, "value": "Petr Nosek"}, 1: {"confidence": 0.41, "value": "Petr Svoboda"}}

def test_get_match_merging_same_drop():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {  "_last_id": 0, 
        id: { "model": model, 
            "contacts_dict": {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}, 
            "contacts_list":  ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'] }    }
        json.dump(models, models_file)
    response = {"entities": [ 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr Nosek", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr Svoboda", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 16, 25 ], "value": "Petr Svoboda", "confidence": 0.7 }
        ], 
        "input": "" }
    nematch = ne_matcher.NEMatcher()

    # when merging occurances of same entity, confidence is the higher one
    # "Petr Nosek" is subset of "Petr Svoboda", so it is dropped
    assert nematch.get_match(id, response, None, None) == {1: {"confidence": 0.83, "value": "Petr Svoboda"}}

def test_get_match_merging_different():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {  "_last_id": 0, 
        id: { "model": model, 
            "contacts_dict": {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}, 
            "contacts_list":  ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'] }    }
        json.dump(models, models_file)
    response = {"entities": [ 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 16, 25 ], "value": "Svoboda", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 16, 25 ], "value": "Nosek", "confidence": 0.7 }
        ], 
        "input": "" }
    nematch = ne_matcher.NEMatcher()

    # when merging occurances of different entities, confidence is averaged
    # but two ids matched -> confidence is halved
    assert nematch.get_match(id, response, None, None) == {1: {"confidence": 0.41, "value": "Petr Svoboda"}, 4: {'confidence': 0.38, 'value': 'Petr Nosek'}}

def test_get_match_merging_different_split():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {  "_last_id": 0, 
        id: { "model": model, 
            "contacts_dict": {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}, 
            "contacts_list":  ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'] }    }
        json.dump(models, models_file)
    response = {"entities": [ 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 16, 21 ], "value": "Nový", "confidence": 0.7 }, 
        ], 
        "input": "" }
    nematch = ne_matcher.NEMatcher()

    # merging occurances of different entities -> confidence is averaged = 0.76
    # closest are "Petrovi" and "Petr Nosek" both with distance 3 -> both get confidence 0.38, which is lower than 0.4 and are dropped
    # that is probably right, since we have no Petr Nový in contacts
    assert nematch.get_match(id, response, None, None) == dict()

def test_split_input_starts_ends():
    input = "Nějaký testovací string obsahující slova."
    words = ['Nějaký', 'testovací', 'string', 'obsahující', 'slova.']
    starts = {0: 0, 7: 1, 17: 2, 24: 3, 35: 4}
    ends = {6: 0, 16: 1, 23: 2, 34: 3, 41: 4}
    assert ne_matcher.split_input_starts_ends(input) == (words, starts, ends)

def test_fuzzy_match_word_to_contacts():
    word = "Jiřímu"
    contacts_dict = {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}
    contacts_list = ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová']
    edit_limit = 4

    # Finds "Jiří" with distance 2 -> confidence is 0.5*(4-2/4)*0.5 = 0.75
    assert ne_matcher.fuzzy_match_word_to_contacts(word, contacts_dict, contacts_list, edit_limit) == {'Jiří Novotný': 0.75}

def test_find_contacts_around_next():
    input = "Pošli 300 Petru Noskovi"
    entities = {'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 15), 'confidence': 0.9}, 'Petr Nosek': {'value': 'Petr Nosek', 'location': (10, 15), 'confidence': 0.9}}
    contacts_dict = {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}
    contacts_list = ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová']
    edit_limit = 3

    # Nosek was not recognized by WA, added by the function, location widened and confidence highered
    assert ne_matcher.find_contacts_around(input, entities, contacts_dict, contacts_list, edit_limit) == {'Petr Svoboda': 
                                                                                                                {'value': 'Petr Svoboda', 'location': (10, 15), 'confidence': 0.9}, 
                                                                                                            'Petr Nosek': 
                                                                                                                {'value': 'Petr Nosek', 'location': (10, 23), 'confidence': 0.95}}

def test_find_contacts_around_previous():
    input = "Pošli 300 Řehoři Peříškovi"
    # WA recognized from surname
    entities = {'Řehoř Peříšek': {'value': 'Řehoř Peříšek', 'location': (17, 27), 'confidence': 0.8}}
    contacts_dict = {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}
    contacts_list = ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová']
    edit_limit = 3

    # matches also the name not recognized before
    assert ne_matcher.find_contacts_around(input, entities, contacts_dict, contacts_list, edit_limit) == {'Řehoř Peříšek': {'value': 'Řehoř Peříšek', 'location': (10, 27), 'confidence': 0.81}}

def test_get_match_whole_with_fuzzy():
    id = "0"
    model = "test0"
    with open("models.json", encoding="utf-8", mode="w+") as models_file:
        models = {  "_last_id": 0, 
        id: { "model": model, 
            "contacts_dict": {'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]}, 
            "contacts_list":  ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'] }    }
        json.dump(models, models_file)
    response = {"entities": [ 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr", "confidence": 0.9 },
        ], 
        "input": "Pošli 300 Petru Noskovi" }
    nematch = ne_matcher.NEMatcher()
    assert nematch.get_match(id, response, None, None) == {4: {'confidence': 0.95, 'value': 'Petr Nosek'}}
