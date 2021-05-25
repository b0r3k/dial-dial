import entities

def test_parse_merge_same_entities():
    response = {"entities": [ 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr Nosek", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 10, 15 ], "value": "Petr Svoboda", "confidence": 0.83 }, 
        { "entity": "name", "location": [ 16, 25 ], "value": "Petr Svoboda", "confidence": 0.7 },
        { "entity": "price", "location": [ 2, 7 ], "value": "cheap", "confidence": 0.9 },
        ] }

    assert entities.parse_merge_same_entities(response) == {
                                                            'name': {'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 25), 'confidence': 0.83}, 'Petr Nosek': {'value': 'Petr Nosek', 'location': (10, 15), 'confidence': 0.83}}, 
                                                            'price': {'cheap': {'value': 'cheap', 'location': (2, 7), 'confidence': 0.9}}
                                                        }

def test_get_entity_starts_ends_mapping():
    ents = {
            'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 25), 'confidence': 0.83}, 
            'Petr': {'value': 'Petr', 'location': (10, 15), 'confidence': 0.9},
            'Nosek': {'value': 'Nosek', 'location': (16, 25), 'confidence': 0.83},
            'Jan Novotný': {'value': 'Jan Novotný', 'location': (30, 42), 'confidence': 0.7},
            'Jan': {'value': 'Jan', 'location': (30, 34), 'confidence': 0.8},
            'Novotný': {'value': 'Novotný', 'location': (35, 42), 'confidence': 0.8}
        }

    assert entities.get_entity_starts_ends_mapping(ents) == ({10: ['Petr Svoboda', 'Petr'], 16: ['Nosek'], 30: ['Jan Novotný', 'Jan'], 35: ['Novotný']},
                                                                {25: ['Petr Svoboda', 'Nosek'], 15: ['Petr'], 42: ['Jan Novotný', 'Novotný'], 34: ['Jan']})

def test_merge_different_consecutive():
    ents = {
            'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 25), 'confidence': 0.83}, 
            'Petr': {'value': 'Petr', 'location': (10, 15), 'confidence': 0.9},
            'Nosek': {'value': 'Nosek', 'location': (16, 25), 'confidence': 0.83},
            'Jan Novotný': {'value': 'Jan Novotný', 'location': (30, 42), 'confidence': 0.7},
            'Jan': {'value': 'Jan', 'location': (30, 34), 'confidence': 0.8},
            'Novotný': {'value': 'Novotný', 'location': (35, 42), 'confidence': 0.8}
        }
    starts = {10: ['Petr Svoboda', 'Petr'], 16: ['Nosek'], 30: ['Jan Novotný', 'Jan'], 35: ['Novotný']}
    ends = {25: ['Petr Svoboda', 'Nosek'], 15: ['Petr'], 42: ['Jan Novotný', 'Novotný'], 34: ['Jan']}

    assert entities.merge_different_consecutive(ents, starts, ends) == {
                                                                            'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 25), 'confidence': 0.83}, 
                                                                            'Jan Novotný': {'value': 'Jan Novotný', 'location': (30, 42), 'confidence': 0.8}, 
                                                                            'Petr Nosek': {'value': 'Petr Nosek', 'location': (10, 25), 'confidence': 0.86}
                                                                        }

def test_drop_subsets():
    ents = {
            'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 25), 'confidence': 0.83}, 
            'Petr': {'value': 'Petr', 'location': (10, 15), 'confidence': 0.9},
            'Nosek': {'value': 'Nosek', 'location': (16, 25), 'confidence': 0.83},
            'Jan Novotný': {'value': 'Jan Novotný', 'location': (30, 42), 'confidence': 0.7},
            'Jan': {'value': 'Jan', 'location': (30, 34), 'confidence': 0.8},
            'Novotný': {'value': 'Novotný', 'location': (35, 42), 'confidence': 0.8}
        }
    starts = {10: ['Petr Svoboda', 'Petr'], 16: ['Nosek'], 30: ['Jan Novotný', 'Jan'], 35: ['Novotný']}
    ends = {25: ['Petr Svoboda', 'Nosek'], 15: ['Petr'], 42: ['Jan Novotný', 'Novotný'], 34: ['Jan']}

    assert entities.drop_subsets(ents, starts, ends) == {
                                                            'Petr Svoboda': {'value': 'Petr Svoboda', 'location': (10, 25), 'confidence': 0.83},
                                                            'Jan Novotný': {'value': 'Jan Novotný', 'location': (30, 42), 'confidence': 0.7}
                                                        }

                                                  