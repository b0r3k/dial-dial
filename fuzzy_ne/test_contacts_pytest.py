import contacts

def test_wa_contacts_to_dict_and_list():
    conts = [ 
        { "type": "synonyms", "value": "Řehoř Peříšek", "synonyms": [ "Řehoř", "Peříšek", "Řepa" ] },
        { "type": "synonyms", "value": "Petr Svoboda", "synonyms": [ "Peťa", "Petr", "Svoboda", "Petru", "Petrovi", "Svobodovi" ] },
        { "type": "synonyms", "value": "Marie Dvořáková", "synonyms": [ "Máňa", "Marie", "Dvořáková" ] },
        { "type": "synonyms", "value": "Jiří Novotný", "synonyms": [ "Jirka", "Jiří", "Novotný" ] },
        { "type": "synonyms", "value": "Petr Nosek", "synonyms": [ "Petr", "Nosek", "Petru", "Petrovi", "Noskovi" ] },
        { "type": "synonyms", "value": "Jan Novák", "synonyms": [ "Honza", "Jenda", "Jan", "Novák" ] },
        { "type": "synonyms", "value": "Jana Černá", "synonyms": [ "Jana", "Černá" ] },
        { "type": "synonyms", "value": "Karolína Machová", "synonyms": [ "Kája", "Karolína", "Machová" ] }
      ]
    
    assert contacts.wa_contacts_to_dict_and_list(conts) == ({'Řehoř Peříšek': [0], 'Řehoř': [0], 'Peříšek': [0], 'Řepa': [0], 'Petr Svoboda': [1], 'Peťa': [1], 'Petr': [1, 4], 
                                                            'Svoboda': [1], 'Petru': [1, 4], 'Petrovi': [1, 4], 'Svobodovi': [1], 'Marie Dvořáková': [2], 'Máňa': [2], 'Marie': [2], 
                                                            'Dvořáková': [2], 'Jiří Novotný': [3], 'Jirka': [3], 'Jiří': [3], 'Novotný': [3], 'Petr Nosek': [4], 'Nosek': [4], 
                                                            'Noskovi': [4], 'Jan Novák': [5], 'Honza': [5], 'Jenda': [5], 'Jan': [5], 'Novák': [5], 'Jana Černá': [6], 'Jana': [6], 
                                                            'Černá': [6], 'Karolína Machová': [7], 'Kája': [7], 'Karolína': [7], 'Machová': [7]},
    
                                                            ['Řehoř Peříšek', 'Petr Svoboda', 'Marie Dvořáková', 'Jiří Novotný', 'Petr Nosek', 'Jan Novák', 'Jana Černá', 'Karolína Machová'])