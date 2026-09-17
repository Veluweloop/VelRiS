from urllib import response

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

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("API did not return valid JSON.")
        return None

def insert_doorkomsten(doorkomsten, api, api_key):
    """
    Send multiple doorkomsten to the API in one request.

    doorkomsten should be a list of dictionaries, for example:

    [
        {
            "EVENEMENT_ID": 123,
            "etappeVolgnummer": 1,
            "ploegNummer": 12,
            "doorkomstTijd": "2026-08-20T21:54:06+02:00"
        },
        ...
    ]

    Returns the decoded JSON response, or None if the request failed.
    """

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            api,
            json=doorkomsten,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"Error while sending doorkomsten: {e}")
        return None

    except ValueError as e:
        print(f"Error while decoding API response: {e}")
        return None

def insert_consequentie_mv(EVENEMENT_ID, etappeVolgnummer, ploegNummer, api, api_key):
    # format for doorkomsttijd: "YYYY-MM-DDTHH:MM:SS"
    payload = {
        "EVENEMENT_ID": EVENEMENT_ID,
        "etappeVolgnummer": etappeVolgnummer,
        "ploegNummer": ploegNummer,
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    response = requests.post(url=api, json=payload, headers=headers, timeout=10)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("API did not return valid JSON.")
        return None

def insert_consequenties_batch(consequenties, api, api_key):
    """
    Send multiple consequenties to the API in one request.
    """

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            api,
            json=consequenties,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"Error while sending consequenties: {e}")
        return None

    except ValueError as e:
        print(f"Error while decoding API response: {e}")
        return None

# Nog bedenken hoe om te gaan met de startnummers welke ploeg, etappe afhankelijk zijn
# ik heb hiervoor de tabel ploeg_startnummer nodig, dan is het goed te doen
def update_doorkomst(DOORKOMST_ID, EVENEMENT_ID, etappeVolgnummer, ploegNummer, startnummer,doorkomstTijd, api, api_key):
    None







# functie voor het opvragen van alle evenementen vanuit de server
def load_events(api):
    response = requests.get(url=api, timeout=10)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("API did not return valid JSON.")
        return None

# functie voor het opvragen van de ploeglijst, etappe's en in de databse te stoppen
def load_competitioninfo(EVENEMENT_ID, api, api_key):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    response = requests.get(url=api, params={"EVENEMENT_ID": EVENEMENT_ID}, headers=headers, timeout=10)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("API did not return valid JSON.")
        return None

def ping_webserver(WPP_name, event_id, checkpoint_id, ping_interval, api, api_key):
    payload = {
        "WISSELPUNTPLOEG": WPP_name,
        "EVENEMENT_ID": event_id,
        "WISSELPUNT_ID": checkpoint_id,
        "PING_INTERVAL": ping_interval
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    response = requests.post(url=api, json=payload, headers=headers, timeout=10)

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print("API did not return valid JSON.")
        return None

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
