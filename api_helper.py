import requests

def insert_doorkomst(EVENEMENT_ID, etappeVolgnummer, ploegNummer, doorkomstTijd, api, api_key):
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

    response = requests.post(api=api, json=payload, headers=headers, timeout=10)    

    return(response.json())