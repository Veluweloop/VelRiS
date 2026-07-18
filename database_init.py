import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("Veluweloop_DB")
EXPORT_DIR = Path(__file__).with_name("exports")


def create_tables():
    # sql code nog loskoppelen van de rest van de code, zodat het makkelijker is om de database te wijzigen
    with sqlite3.connect(DB_PATH) as conn:
        # maken van de tabel voor de doorkomsten
        # besluiten of de registraties van andere wisselpunten vanuit de remote databasde ook in deze tabel komen
        conn.execute('''
          CREATE TABLE IF NOT EXISTS DOORKOMSTEN(
          ID_LOCAL INTEGER NOT NULL PRIMARY KEY,
          ID_SERVER INTEGER,
          DATETIME TEXT NOT NULL,
          PLOEG INTEGER NOT NULL,
          ID_LOCATIE INTEGER NOT NULL,
          STATUS TEXT NOT NULL,
          EVENEMENT_ID INTEGER NOT NULL DEFAULT -1,
          LOCAL_CHANGE INTEGER NOT NULL DEFAULT 1
          )
        ''')

        conn.execute('''
          CREATE TABLE IF NOT EXISTS WISSELPUNTEN(
          ID INTEGER NOT NULL PRIMARY KEY,
          WISSELPUNT_NAAM TEXT NOT NULL,
          ETAPPE_VOLGNUMMER INTEGER NOT NULL,
          EVENEMENT_ID INTEGER NOT NULL DEFAULT -1
          )
      ''')

        conn.execute('''             
          CREATE TABLE IF NOT EXISTS PLOEGLIJST(
          PLOEG_ID INTEGER NOT NULL PRIMARY KEY,
          PLOEGNUMMER INTEGER NOT NULL,
          PLOEG_NAAM TEXT NOT NULL,
          EVENEMENT_ID INTEGER NOT NULL DEFAULT -1
          )
      ''')

        conn.execute('''             
          CREATE TABLE IF NOT EXISTS EVENEMENTEN(
          EVENEMENT_ID INTEGER NOT NULL PRIMARY KEY,
          EVENEMENT_NAAM TEXT NOT NULL
          )
      ''')

def insert_doorkomst(datetime, ploeg, id_locatie, status, evenement_id, id_local=None, id_server=None, local_change=True):
    with sqlite3.connect(DB_PATH) as conn:
        local_change_flag = 1 if local_change else 0
        if id_local is None:
            conn.execute('''
              INSERT INTO DOORKOMSTEN (ID_SERVER, DATETIME, PLOEG, ID_LOCATIE, STATUS, EVENEMENT_ID, LOCAL_CHANGE)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (id_server, datetime, ploeg, id_locatie, status, evenement_id, local_change_flag))
        else:
            conn.execute('''
              INSERT INTO DOORKOMSTEN (ID_LOCAL, ID_SERVER, DATETIME, PLOEG, ID_LOCATIE, STATUS, EVENEMENT_ID, LOCAL_CHANGE)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
              ON CONFLICT(ID_LOCAL) DO UPDATE SET
                ID_SERVER = excluded.ID_SERVER,
                DATETIME = excluded.DATETIME,
                PLOEG = excluded.PLOEG,
                ID_LOCATIE = excluded.ID_LOCATIE,
                STATUS = excluded.STATUS,
                EVENEMENT_ID = excluded.EVENEMENT_ID,
                LOCAL_CHANGE = excluded.LOCAL_CHANGE
            ''', (id_local, id_server, datetime, ploeg, id_locatie, status, evenement_id, local_change_flag))

def insert_wisselpunt(wisselpunt_id, wisselpunt_naam, etappe_volgnummer, evenement_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
          INSERT INTO WISSELPUNTEN (ID, WISSELPUNT_NAAM, ETAPPE_VOLGNUMMER, EVENEMENT_ID)
          VALUES (?, ?, ?, ?)
          ON CONFLICT(ID) DO UPDATE SET
            WISSELPUNT_NAAM = excluded.WISSELPUNT_NAAM,
            ETAPPE_VOLGNUMMER = excluded.ETAPPE_VOLGNUMMER,
            EVENEMENT_ID = excluded.EVENEMENT_ID
        ''', (wisselpunt_id, wisselpunt_naam, etappe_volgnummer, evenement_id))

def insert_ploeg(ploeg_id, ploegnummer, ploeg_naam, evenement_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
          INSERT INTO PLOEGLIJST (PLOEG_ID, PLOEGNUMMER, PLOEG_NAAM, EVENEMENT_ID)
          VALUES (?, ?, ?, ?)
          ON CONFLICT(PLOEG_ID) DO UPDATE SET
            PLOEGNUMMER = excluded.PLOEGNUMMER,
            PLOEG_NAAM = excluded.PLOEG_NAAM,
            EVENEMENT_ID = excluded.EVENEMENT_ID
        ''', (ploeg_id, ploegnummer, ploeg_naam, evenement_id))

def insert_evenement(evenement_id, evenement_naam):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
          INSERT INTO EVENEMENTEN (EVENEMENT_ID, EVENEMENT_NAAM)
          VALUES (?, ?)
          ON CONFLICT(EVENEMENT_ID) DO UPDATE SET
            EVENEMENT_NAAM = excluded.EVENEMENT_NAAM
        ''', (evenement_id, evenement_naam))


def print_schema():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        print("TABELLEN:", tables)
        for t in tables:
            print("---", t, "---")
            print(cur.execute(f"PRAGMA table_info({t})").fetchall())
    finally:
        conn.close()

def export_all_tables_to_csv(output_dir=None):
    if output_dir is None:
        output_dir = EXPORT_DIR

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

        for table_name in tables:
            rows = cur.execute(f"SELECT * FROM {table_name}").fetchall()
            columns = [col[1] for col in cur.execute(f"PRAGMA table_info({table_name})")]

            csv_path = output_dir / f"{table_name.lower()}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(columns)
                writer.writerows(rows)

            print(f"Exported {table_name} -> {csv_path}")
    finally:
        conn.close()

if __name__ == "__main__":
    print_schema()
    export_all_tables_to_csv()

