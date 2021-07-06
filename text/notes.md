# BP

- [BP](#bp)
  - [1. Úvod](#1-úvod)
  - [2. Dialogové systémy](#2-dialogové-systémy)
    - [2.1 Historie?](#21-historie)
    - [2.2 Task-oriented](#22-task-oriented)
    - [2.3 Chit chat](#23-chit-chat)
    - [2.4 Kombinace?](#24-kombinace)
  - [3. Komponenty (NLU->DST->...) vs end-to-end ML?](#3-komponenty-nlu-dst--vs-end-to-end-ml)
  - [4. Hlasoví asistenti](#4-hlasoví-asistenti)
    - [4.1 Historie?](#41-historie)
    - [4.2 Existující](#42-existující)
  - [5. Něco o Levenshtein edit distance někam](#5-něco-o-levenshtein-edit-distance-někam)
    - [5.1 regexy?](#51-regexy)
  - [6. Moje implementace](#6-moje-implementace)
    - [6.1 android app, stt, volání api, tts, zahájení hovoru](#61-android-app-stt-volání-api-tts-zahájení-hovoru)
    - [6.2 Watson, dialog a entity v něm (získání dat)](#62-watson-dialog-a-entity-v-něm-získání-dat)
    - [6.3 NE matching jako webhook v cloudfunction](#63-ne-matching-jako-webhook-v-cloudfunction)
  - [7. Závěr](#7-závěr)
  - [Chytré rady](#chytré-rady)

## 1. Úvod
- Motivace 
    - (nejen) hlasoví asistenti čím dál populárnější
    - v češtině téměř nejsou
    - možnost volat téměř bez dívání/rukou, třeba v autě/při vaření

## 2. Dialogové systémy
- co to je, proč to je
### 2.1 Historie?
- takový ten opakující se jak tam má Jurafsky 
### 2.2 Task-oriented
### 2.3 Chit chat
### 2.4 Kombinace?

## 3. Komponenty (NLU->DST->...) vs end-to-end ML?

## 4. Hlasoví asistenti
### 4.1 Historie?
### 4.2 Existující
- Watson, Google, Siri, Alexa, Cortana, Microft, v autech,..

## 5. Něco o Levenshtein edit distance někam
### 5.1 regexy?

## 6. Moje implementace
- přehled všech komponent
### 6.1 android app, stt, volání api, tts, zahájení hovoru
### 6.2 Watson, dialog a entity v něm (získání dat)
### 6.3 NE matching jako webhook v cloudfunction

## 7. Závěr
- asi něco o tom, že jsem splnil cíl mít aplikaci, která nějak vede dialog, matchne kontakt a zavolá mu
- že to funguje česky, což jinde není

## Chytré rady
- Rozvrhni si celkovou strukturu toho textu a nejdřív si ke každé kapitole/oddílu napiš jen poznámky, co tam chceš mít (jde to rychlejc než psát to načisto). Pak je prostě rozepíšeš do textu.
- Do úvodu sepiš nějakou motivaci (co děláš a proč je to důležitý nebo potřebný), stanov si cíle práce a pak tam dej nějaký "rozcestník po dalších kapitolách"
- Pak by měla následovat nějaká teoretická/přehledová kapitola (vysvětlení pojmů a něco o tom, jak se to implementuje – trochu přehled literatury, ale nemusíš moc do hloubky), pak popis systému, pak experimenty a výsledky
- Nakonec dej nějaké shrnutí a konstatování, co z cílů jsi splnil
- Na úvod každé kapitoly taky dej nějaký "rozcestník" – popis toho, co je v té kapitole (v jednotlivých sekcích)
- Všude explicitně piš, co je tvoje vlastní implementace/experiment a kde jsi použil nějaký existující kód, tohle je potřeba důsledně rozlišovat
- Nevím, jak moc jsi zatím pracoval s BibTeXem, ale určitě se ho neboj :slightly_smiling_face:. Pro lepší citace doporučuju spíš export z DBLP nebo ACL Anthology než Google Scholaru (Scholar je takový trochu neuspořádaný, zas v DBLP/ACL nenajdeš úplně všechno). Docela fajn je si literaturu uspořádat v manažeru bibliografie (já používám Zotero, celkem snadno se do něj importuje z webu pomocí pluginu do browseru a export do BibTeXu je taky jednoduchý) – ale možná, že tohle se hodí až k diplomce, až toho budeš mít víc.
- Dej si bacha, že to celé musí být validní formát PDF/A, aby se to dalo nahrát do SISu (v těch ofiko šablonách na to myslím je balíček, ale některé vložené obrázky to můžou pokazit... SIS na to má validátor). Tohle je asi na později, ale stejně je dobrý o tom vědět.