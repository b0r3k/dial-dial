from collections import defaultdict

# example contacts to work with, format es returned from WA workspace
def return_test_contacts():
    contacts = [
        {
          "type": "synonyms",
          "value": "Řehoř Peříšek",
          "synonyms": [
            "Řehoř",
            "Peříšek",
            "Řepa"
          ]
        },
        {
          "type": "synonyms",
          "value": "Petr Svoboda",
          "synonyms": [
            "Peťa",
            "Petr",
            "Svoboda",
            "Petru",
            "Petrovi",
            "Svobodovi"
          ]
        },
        {
          "type": "synonyms",
          "value": "Marie Dvořáková",
          "synonyms": [
            "Máňa",
            "Marie",
            "Dvořáková"
          ]
        },
        {
          "type": "synonyms",
          "value": "Jiří Novotný",
          "synonyms": [
            "Jirka",
            "Jiří",
            "Novotný"
          ]
        },
        {
          "type": "synonyms",
          "value": "Petr Nosek",
          "synonyms": [
            "Petr",
            "Nosek",
            "Petru",
            "Petrovi",
            "Noskovi"
          ]
        },
        {
          "type": "synonyms",
          "value": "Jan Novák",
          "synonyms": [
            "Honza",
            "Jenda",
            "Jan",
            "Novák"
          ]
        },
        {
          "type": "synonyms",
          "value": "Jana Černá",
          "synonyms": [
            "Jana",
            "Černá"
          ]
        },
        {
          "type": "synonyms",
          "value": "Karolína Machová",
          "synonyms": [
            "Kája",
            "Karolína",
            "Machová"
          ]
        }
      ]
    return contacts

#contacts = return_test_contacts()

def contacts_to_id_dict(contacts):
    """
    Parses entities from WA workspace into dict with contact id as value.

    Parameters:
    contacts (list): List of entities as in WA.list_entities(..).get_result()["entities"][x]["values"].


    Returns:
    cont_id_dict (dict): 
        Dictionary contacts[name] = id, where each "value" end "synonym" is saved as key for given id.
    """
    cont_id_dict = defaultdict(list)
    for id, contact in enumerate(contacts):
        contact_names = [contact["value"]]
        contact_names += contact["synonyms"]
        [cont_id_dict[name].append(id) for name in contact_names]
    return cont_id_dict

#cont_id_dict = contacts_to_id_dict(contacts)
#print(cont_id_dict)