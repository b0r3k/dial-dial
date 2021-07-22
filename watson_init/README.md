# Dokumentace 

Tato část slouží k nastavení instance asistenta IBM Watson (dále WA) pomocí skriptů. Pro funkčnost je potřeba mít v této složce autentizační soubor `ibm-credentials.env` stažený z webového prostředí IBM.

## Získání jmen

Pro nahrání do WA jsme potřebovali získat česká jména. To zajišťuje skript `czech_names/names.py` pracující s daty ze stránky MVČR z roku 2018. Pomocí knihovny `pandas` jsme data převedli na formát `csv` a následně z nich vybrali všechna jména a příjmení, která mělo v době sběru dat alespoň 200 lidí. Získaná jména a příjmení jsme uložili do souboru `czech_names/names.json` pro jednoduché další zpracování.

## Nastavení instance WA

Nejprve pomocí `workspace.py` vytvoříme v asistentovi prostředí (schopnost). Následně v souboru `intents.py` definujeme uživatelské úmysly, které chceme detekovat, spolu se vzorovými větami. Do WA je nahrajeme pomocí metody `update_workspace`, kterou budeme používat vždy. V souboru `entities.py` definujeme jako entitu jména a data k ní nahrajeme z dříve vytvořeného `czech_names/names.py`. Nakonec v souboru `dialog_nodes.py` definujeme vrcholy pro řízení dialogu.