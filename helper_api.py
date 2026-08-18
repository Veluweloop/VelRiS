import requests

def insert_doorkomst(EVENEMENT_ID, etappeVolgnummer, ploegNummer, doorkomstTijd, api, api_key):
    # format for doorkomsttijd: "YYYY-MM-DDTHH:MM:SS"
    payload = {
        "EVENEMENT_ID": EVENEMENT_ID,
        "etappeVolgnummer": etappeVolgnummer,
        "ploegNummer": ploegNummer,
        "doorkomstTijd": doorkomstTijd
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    response = requests.post(url=api, json=payload, headers=headers, timeout=10)

    # print(f"[insert_doorkomst] status={response.status_code}")
    # print(response.text)

    return response.json()

# Nog bedenken hoe om te gaan met de startnummers welke ploeg, etappe afhankelijk zijn
# ik heb hiervoor de tabel ploeg_startnummer nodig, dan is het goed te doen
def update_doorkomst(DOORKOMST_ID, EVENEMENT_ID, etappeVolgnummer, ploegNummer, startnummer,doorkomstTijd, api, api_key):
    None

# functie voor het opvragen van alle evenementen vanuit de server
def load_events(api):
    response = requests.get(url=api, timeout=10)

    return response.json()

# functie voor het opvragen van de ploeglijst, etappe's en in de databse te stoppen
def load_competitioninfo(EVENEMENT_ID, api, api_key):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    response = requests.get(url=api, params={"EVENEMENT_ID": EVENEMENT_ID}, headers=headers, timeout=10)

#    print(response.text)

    return response.json()

if __name__ == "__main__":
    import pprint

    evenement_id = int(input("EVENEMENT_ID: "))
    api_key = input("API_KEY: ")

    print("Calling wedstrijdinfo...")
    pprint.pp(
        load_competitioninfo(
            evenement_id,
            "https://veluweloop.nl/api/wedstrijdinfo.php",
            api_key,
        ),
        width=80,
        sort_dicts=False,
    )

    etappeVolgnummer = int(input("ETAPPE_VOLGNUMMER: "))
    ploegNummer = int(input("PLOEG_NUMMER: "))
    doorkomstTijd = input("DOORKOMST_TIJD: ")

    print("Sending doorkomst...")
    pprint.pp(
        insert_doorkomst(
            evenement_id,
            etappeVolgnummer,
            ploegNummer,
            doorkomstTijd,
            "https://veluweloop.nl/api/doorkomst_invoer.php",
            api_key,
        ),
        width=80,
        sort_dicts=False,
    )
