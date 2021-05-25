from collections import defaultdict



def wa_contacts_to_dict_and_list(contacts):
    """
    Parses entities from WA workspace into dict with contact id as value and corresponding list.

    Parameters:
    contacts (list): List of entities as in WA.list_entities(..).get_result()["entities"][x]["values"].


    Returns:
    cont_id_dict (dict): 
        Dictionary contacts[name] = id, where each "value" end "synonym" is saved as key for given id.
    cont_list (list):
        List contacts[id] = "Name Surname"
    """
    cont_id_dict = defaultdict(list)
    cont_list = list()
    for id, contact in enumerate(contacts):
        value = contact["value"]
        contact_names = [value]
        contact_names += contact["synonyms"]
        [cont_id_dict[name].append(id) for name in contact_names]
        cont_list.append(value)
    return cont_id_dict, cont_list