# Dokumentace

Pro vytvoření aplikace jsme využili integrované vývojové prostředí _Android Studio_. Původním záměrem bylo využít _Visual Studio Code_ spolu s _vývojovými kontejnery_ za použití virtualizačního softwaru _Docker_, především díky přenositelnosti a relativní nenáročnosti na výpočetní výkon. Ukázalo se však, že tato cesta není při vývoji aplikací pro Android v jazyce Kotlin pod operačním systémem Windows úplně běžná a naráží na mnoho komplikací, tedy je především pro začátek silně nevhodná. Pro kompilaci využíváme běžně používaný _gradle_.

V případě zájmu o kompilaci aplikace také doporučujeme otevřít celý projekt v Android Studiu.

Aplikace musela vyřešit několik věcí: získat oprávnění ke všem operacím, získat kontakty uživatele, vytvořit _session_ ve WA a odeslat jména kontaktů, spustit rozpoznání hlasu, po dokončení výsledek odeslat jako zprávu do WA, po získání odpovědi spustit hlasový syntetizátor, po skončení jeho projevu buď spustit rozpoznání hlasu a celý běh znovu, nebo zahájit hovor.

## Celková koncepce a vzhled

Jednotlivé komponenty (obvykle reprezentované jednou obrazovkou) se v aplikacích pro Android nazývají _Activity_. Protože nám stačí jedna obrazovka, je celý kód umístěn v jednom souboru `MainActivity.kt` a jednoduché uživatelské rozhraní v korespondujícím `activity_main.xml`. Pro změnu grafického rozhraní z kódu je třeba jejich propojení, které zajišťuje instance třídy `ActivityMainBinding`. Toto je aktuálně oficiálně doporučený postup (na úkor dříve používaného vyhledání pomocí `id`), ale vygenerování propojovací třídy musíme povolit v souboru `build.gradle` na úrovni modulu.

Tato instance je využita při otevření aplikace pro vytvoření grafického rozhraní ze zdroje a následně v kódu kdykoliv chceme k rozhraní přistupovat. To v našem případě znamená nastavení reakce na stisk tlačítka, případně jeho deaktivace či změna vzhledu pro indikaci probíhajících procesů.

Veškeré grafické prvky jsou uloženy ve složkách `res/drawable*`. Texty, které zobrazujeme, jsou pro jednodušší centrální editaci uloženy v souboru `res/values/strings.xml`.

Pro zobrazování krátkých hlášení uživateli využíváme tzv. `Toast` notifikace, které po chvíli samy zmizí.

## Získání oprávnění

Pro svou správnou funkci potřebuje aplikace povolení nahrávat zvuk, číst kontakty, vykonávat hovory a přistupovat k internetu. Všechna požadovaná oprávnění musí být uvedena v souboru `AndroidManifest.xml`, první tři jsou navíc oprávněními za času běhu, tedy o ně musíme explicitně požádat. Oprávnění k přístupu k internetu není pro Android tak zásadní (především protože neoperuje s uživatelovými daty), tedy je automaticky uděleno při instalaci aplikace.

Aktuálně oficiálně doporučeným postupem (který z toho důvodu využíváme), jak řešit oprávnění, je nejprve o ně požádat, pokud uživatel odmítne a pokusí se aplikaci znovu použít, zobrazit vysvětlení, k čemu jsou nutná a znovu o ně požádat, a pokud znovu odmítne, již jen ukazovat upozornění o nedostupnosti.

Ověření získání oprávnění (případně zda už jsme o ně žádali) zajišťuje funkce `checkPermissions`.

Pro požádání o oprávnění potřebujeme spustit jinou aktivitu (pro získání oprávnění existuje jedna vestavěná), vyčkat na její výsledek a na základě něj rozhodnout o dalších krocích. K tomu využíváme opět aktuálně doporučenou metodu `registerForActivityResult`, kterou s tímto callbackem uložíme do proměnné `requestPermissionLauncher`. Pro zobrazení vysvětlení potřeby oprávnění i upozornění o nedostupnosti využíváme třídu `AlertDialog` v metodách `showRationaleDialog` a `showUnavailableDialog`.

## Získání kontaktů

Kontakty potřebujeme získat z úložiště telefonu, které se chová podobně jako databáze. Proto dotaz na ně začneme pomocí funkce `loadContacts` na začátku inicializace celé služby WA asynchronně jako koprogram. V rámci něj pak získáme jména a čísla kontaktů, které uložíme do slovníku.

## Vytvoření session ve WA a odeslání jmen kontaktů 

Po začátku dotazu na kontakty zavoláme metodu `tryPrepareWatson`, ve které vytvoříme instanci třídy `Assistant` z IBM Java SDK pro komunikaci s WA API. Té předáme potřebné parametry a následně pošleme požadavek pro zahájení session. V Androidu není možné posílat síťové požadavky v hlavním vlákně (protože je potřeba udržovat ho volné pro UI), takže s výhodou opět použijeme běh jako koprogram. Následně pomocí `await` zajistíme kontrolu dokončení získávání kontaktů a předáme je jako _kontext_ do WA session. Pokud se v průběhu něco nepovede, výjimku odchytíme a příště se pokusíme provést celou inicializaci znovu.

Původní záměr byl odesílat kontakty do WA jako standardní zprávu, jenže tam jsme brzy narazili na limit velikosti požadavku 2048 znaků. Delší seznam kontaktů se do tohoto limitu nevejde, proto jsme nakonec využili nastavení kontextu.

Důležité je ještě zmínit, že parametry pro komunikaci s WA musí být uloženy zvlášť v souboru `res/values/credentials.xml` a nejsou součástí repositáře.

## Spuštění rozpoznávání hlasu

Obdobně jako u získání oprávnění potřebujeme spustit nějakou aktivitu a získat její výsledek, tedy využijeme `registerForActivityResult`. Pro rozpoznání řeči nenajdeme vestavěnou aktivitu, ale můžeme využít parametr `Intent` (úmysl) při spuštění. Protože ho potřebujeme používat často, vytvoříme ho jen jednou při otevření aplikace a předáme mu potřebné parametry (český jazyk, jeden výsledek, atp.). Když aktivita spuštěná s tímto úmyslem skončí, zkontrolujeme, že proběhla úspěšně a pokračujeme k dalšímu kroku.

## Odeslání do WA a získání odpovědi
Opět pomocí `await` vyčkáme nachystání WA. Pokud je vše připraveno, pošleme v koprogramu (jedná se o síťový požadavek) text do WA pomocí metody `getWatsonResponse` a získáme odpověď. Tuto odpověď ještě zpracujeme, pokud je na prvním řádku `[call]`, jedná se o pokyn k hovoru od WA, na druhém řádku najdeme jméno kontaktu a na třetím text k přečtení. Pomocí jména  kontaktu zjistíme jeho číslo, vytvoříme `Intent` volání a nastavením proměnné `launchAgain` na `false` uložíme, že dialog skončil. V opačném případě pošleme celou odpověď k přečtení.

## Spuštění hlasového syntetizátoru

Převod textu na řeč budeme také potřebovat používat často, proto instanci třídy `TextToSpeech` též vytvoříme při otevření programu. Nastavíme ji na český jazyk a přepíšeme v ní funkci `onDone`, která je spuštěna, když skončí přehrávání hlasu. Pokud dialog neskončil, spustíme celý běh od rozpoznání hlasu zabalený ve funkci `launchPipeline` znovu. Pokud skončil, jsme připraveni začít volat, vytočíme tedy číslo a ukončíme session ve WA i celou aplikaci.