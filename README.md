[Český popis](#-vytáčeč)

# 📞 Dialog Dialer

Voice assistant in Czech language for placing calls from Android phone. Built using IBM Watson, Google STT/TTS, Kotlin and Python. Bachelor thesis at MFF UK.

## How to help?

Try the app (**in Czech only**) and describe your experience in a [short questionnaire](https://forms.office.com/r/37GhdkZQAq). Thanks a lot!

## How it looks?

You can watch preview on youtube:

https://youtu.be/Wx7mFsZIWF0

## How to install it?

Download .apk from Releases section [here](https://github.com/b0r3k/dial-dial/releases/latest/download/dialog_dialer.apk) and install it to 
a phone with Android 6.0 or higher. You'll see some warnings, because I didn't pay the fee to publish on Google Play, but all the source code 
is in this repository.

## How it works?

The app sends the user's input to IBM Watson Assistant which decides, what's next. If it's time to match the name with contacts, matching component is called. 
The Watson's response is read back in the app and the call is started if desired.

### Application part

After the button press the permissions are resolved. If the app gets all the permissions, speech to text is started. Result is sent to Watson, from which answer 
is get. The answer is read by text to speech synthesizer. Call is started and application ended if desired, otherwise speech to text and the whole pipeline is 
launched again.

### Watson asistent

Detects *intents* and *entities*, based on them returns a response. After detecting that user wants to call and that name was stated, calls the matching component. 
If it gets only one name back, prompts the app to start the call. If it gets more names, asks the user which one he meant.

### Matching component

Uses the entities detected by Watson. Tries to match with each contact name using Levenshtein distance ("how similar the two words are"). Looks also at the original 
input, possibly detecting what Watson missed. If it is sure with a single contact (the one has ˙confidence` at least `0.1` higher than the rest), returns only that 
one. Otherwise returns everything matched.



# 📞 Vytáčeč

Hlasový asistent pro zahájení hovoru s lidmi uloženými ve vašich kontaktech, aplikace pro Android. Využívá nástrojů IBM Watson a Google STT/TTS, 
programovacích jazyků Kotlin a Python. Bakalářská práce na MFF UK.

## Jak mi pomoct?

Vyzkoušejte aplikaci a své zkušenosti popište v [krátkém dotazníku](https://forms.office.com/r/37GhdkZQAq). Děkuji!

## Jak to vypadá?

Preview můžete najít na youtube:

https://youtu.be/Wx7mFsZIWF0

## Jak ho nainstalovat?

Stáhněte si .apk ze sekce Releases [zde](https://github.com/b0r3k/dial-dial/releases/latest/download/dialog_dialer.apk) a nainstalujte do telefonu 
se systémem Android 6.0 nebo vyšším. Objeví se varování, protože jsem nezaplatil za možnost publikovat aplikaci na Google Play, ale veškerý zdrojový kód 
je v tomto repozitáři.

## Jak to funguje?

Aplikace pošle text od uživatele do asistenta IBM Watson, který vyhodnotí, co dál. Pokud je čas porovnat udané jméno s kontakty, zavolá porovnávací komponentu. 
Odpověď je přečtena zpět v aplikaci, případně je zahájen hovor.

### Aplikační část

Po stisknutí tlačítka jsou vyřešna oprávnění. Pokud aplikace dostane dostatečná oprávnění, je zahájeno rozpoznávání hlasu. Výsledek putuje do asistenta Watson, 
ze kterého je získána odpověď. Ta je přečtena hlasovým syntetizátorem. Pokud má být začat hovor, stane se tak a aplikace je ukončena. Pokud ne, je znovu spuštěno 
rozpoznávání hlasu a celý koloběh.

### Watson asistent

Obsahuje detekci *úmyslů* a *entit*, ale především rozhodovací strom dialogu. Na základě detekovaného vrací jednu z možných odpovědí. Pokud usoudí, že uživatel 
chce volat a řekl jméno, zavolá porovnávací komponentu, která jméno porovná se seznamem kontaktů. Pokud ta si je dostatečně jista konkrétní osobou, vrátí její 
jméno a Watson sdělí aplikaci, že této osobě se má zavolat. Pokud komponenta vrátí více jmen, Watson se uživatele zeptá, které z nich myslel.

### Porovnávací komponenta

Využívá entity, které rozpoznal Watson. Snaží se najít kontakt, který této entitě nejvíce odpovídá. K tomu využívá Levenshteinovu vzdálenost (kolik úprav musíme 
u jednoho slova udělat, abychom dostali druhé). Nedívá se jen na entitu, kterou poznal Watson, ale i do originálního vstupu, takže může využít i příjmení, které 
Watson nerozeznal. Pokud jeden kontakt odpovídá výrazně více než zbylé (má `confidence` alespoň o `0.1` vyšší), vrátí jen ten. Jinak vrátí všechny "dostatečně" 
odpovídající.
