# VelRiS
Welkom bij VelRiS (Veluweloop Registratie Systeem). Het is een python/Flask app voor de wisselpuntploegwn tijdens de Veluweloop. De primaire functie is het invoeren van de doorkomsten en deze doorsturen naar de centrale database.aanvullende opties zijn het inzien van de nog niet geregistreerde ploegen, invoeren van consequenties en het wijzigen van doorkomsten.

## Installatie 
de app is gebouwd op basis van Flask met Python 3. Er moet nog een requirements/toml file aangemaakt worden om de installatie makkelijker te maken. Naast python/Flask zijn er geen extra afhankelijkheden welke niet via pup geïnstalleerd kunnen worden.

## eerste keer gebruik
Bij de eerste keer gebruik (en het wisselen van evenementen) is een internetverbinding noodzakelijk. De app kan gestart worden door main.py te starten. Er is ook een batchfile (@@) beschikbaar waarmee de app gestart kan worden. De gebruikersinterface is gebouwd op basis van html (webbrowser) en na het opstarten van de app kan de gebruikersinterface gestart worden in de browser via localhost:5000

## installatie lubuntu
sudo apt install -y git python3 python3-pip python3-venv python3-tk curl firefox

chmod +x start-kiosk.sh stop-kiosk.sh install.sh

small update: git pull

### hard update
git fetch origin
git reset --hard origin/main

## Systeem opbouw
### main.py

### webapp

### helpers

