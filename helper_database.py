import csv
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("Veluweloop_DB")
EXPORT_DIR = Path(__file__).with_name("exports")

def create_tables():
    # sql code nog loskoppelen van de rest van de code, zodat het makkelijker is om de database te wijzigen
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        # maken van de tabel voor de doorkomsten
        # besluiten of de registraties van andere wisselpunten vanuit de remote databasde ook in deze tabel komen
        conn.execute('''
          CREATE TABLE IF NOT EXISTS DOORKOMSTEN(
          ID_LOCAL INTEGER NOT NULL PRIMARY KEY,
          ID_SERVER INTEGER,
          DATETIME TEXT NOT NULL,
          PLOEG INTEGER NOT NULL,
          ETAPPE_VOLGNUMMER INTEGER NOT NULL,
          STATUS TEXT NOT NULL,
          EVENEMENT_ID INTEGER NOT NULL DEFAULT -1,
          LOCAL_CHANGE INTEGER NOT NULL DEFAULT 1
          )
        ''')

        conn.execute('''
                CREATE TABLE IF NOT EXISTS CONSEQUENTIES(
                ID_LOCAL INTEGER NOT NULL PRIMARY KEY,
                ID_SERVER INTEGER,
                DATETIME TEXT NOT NULL,
                PLOEG INTEGER NOT NULL,
                ETAPPE_VOLGNUMMER INTEGER NOT NULL,
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

        conn.execute('''             
              CREATE TABLE IF NOT EXISTS INSTELLINGEN(
              INSTELLING_ID INTEGER NOT NULL PRIMARY KEY,
              INSTELLING_NAAM TEXT NOT NULL UNIQUE,
              INSTELLING_WAARDE TEXT NOT NULL
              )
          ''')

def clear_wisselpunten():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('DELETE FROM WISSELPUNTEN')

def clear_doorkomsten():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('DELETE FROM DOORKOMSTEN')

def clear_ploeglijst():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('DELETE FROM PLOEGLIJST')

def clear_evenementen():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('DELETE FROM EVENEMENTEN')

def clear_instellingen():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('DELETE FROM INSTELLINGEN')

def insert_doorkomst(datetime, ploeg, ETAPPE_VOLGNUMMER, status, evenement_id, id_local=None, id_server=None, local_change=True):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        local_change_flag = 1 if local_change else 0
        if id_local is None:
            conn.execute('''
              INSERT INTO DOORKOMSTEN (ID_SERVER, DATETIME, PLOEG, ETAPPE_VOLGNUMMER, STATUS, EVENEMENT_ID, LOCAL_CHANGE)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (id_server, datetime, ploeg, ETAPPE_VOLGNUMMER, status, evenement_id, local_change_flag))
        else:
            conn.execute('''
              INSERT INTO DOORKOMSTEN (ID_LOCAL, ID_SERVER, DATETIME, PLOEG, ETAPPE_VOLGNUMMER, STATUS, EVENEMENT_ID, LOCAL_CHANGE)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
              ON CONFLICT(ID_LOCAL) DO UPDATE SET
                ID_SERVER = excluded.ID_SERVER,
                DATETIME = excluded.DATETIME,
                PLOEG = excluded.PLOEG,
                ETAPPE_VOLGNUMMER = excluded.ETAPPE_VOLGNUMMER,
                STATUS = excluded.STATUS,
                EVENEMENT_ID = excluded.EVENEMENT_ID,
                LOCAL_CHANGE = excluded.LOCAL_CHANGE
            ''', (id_local, id_server, datetime, ploeg, ETAPPE_VOLGNUMMER, status, evenement_id, local_change_flag))

def get_doorkomsten(evenement_id=None, etappe_volgnummer=None):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row    
        if evenement_id is None or etappe_volgnummer is None:
            cursor = conn.execute('''
                SELECT *
                FROM DOORKOMSTEN
                ORDER BY DATETIME DESC
            ''')
        else:
            cursor = conn.execute('''
                SELECT *
                FROM DOORKOMSTEN
                WHERE EVENEMENT_ID = ?
                AND ETAPPE_VOLGNUMMER = ?
                ORDER BY DATETIME DESC
            ''', (evenement_id, etappe_volgnummer))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

def insert_consequentie(datetime, ploeg, ETAPPE_VOLGNUMMER, status, evenement_id, id_local=None, id_server=None, local_change=True):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        local_change_flag = 1 if local_change else 0
        if id_local is None:
            conn.execute('''
              INSERT INTO CONSEQUENTIES (ID_SERVER, DATETIME, PLOEG, ETAPPE_VOLGNUMMER, STATUS, EVENEMENT_ID, LOCAL_CHANGE)
              VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (id_server, datetime, ploeg, ETAPPE_VOLGNUMMER, status, evenement_id, local_change_flag))
        else:
            conn.execute('''
              INSERT INTO CONSEQUENTIES (ID_LOCAL, ID_SERVER, DATETIME, PLOEG, ETAPPE_VOLGNUMMER, STATUS, EVENEMENT_ID, LOCAL_CHANGE)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)
              ON CONFLICT(ID_LOCAL) DO UPDATE SET
                ID_SERVER = excluded.ID_SERVER,
                DATETIME = excluded.DATETIME,
                PLOEG = excluded.PLOEG,
                ETAPPE_VOLGNUMMER = excluded.ETAPPE_VOLGNUMMER,
                STATUS = excluded.STATUS,
                EVENEMENT_ID = excluded.EVENEMENT_ID,
                LOCAL_CHANGE = excluded.LOCAL_CHANGE
            ''', (id_local, id_server, datetime, ploeg, ETAPPE_VOLGNUMMER, status, evenement_id, local_change_flag))

def get_consequenties(evenement_id=None, etappe_volgnummer=None):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row    
        if evenement_id is None or etappe_volgnummer is None:
            cursor = conn.execute('''
                SELECT *
                FROM CONSEQUENTIES
                ORDER BY DATETIME DESC
            ''')
        else:
            cursor = conn.execute('''
                SELECT *
                FROM CONSEQUENTIES
                WHERE EVENEMENT_ID = ?
                AND ETAPPE_VOLGNUMMER = ?
                ORDER BY DATETIME DESC
            ''', (evenement_id, etappe_volgnummer))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

def insert_wisselpunt(wisselpunt_id, wisselpunt_naam, etappe_volgnummer, evenement_id):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('''
          INSERT INTO WISSELPUNTEN (ID, WISSELPUNT_NAAM, ETAPPE_VOLGNUMMER, EVENEMENT_ID)
          VALUES (?, ?, ?, ?)
          ON CONFLICT(ID) DO UPDATE SET
            WISSELPUNT_NAAM = excluded.WISSELPUNT_NAAM,
            ETAPPE_VOLGNUMMER = excluded.ETAPPE_VOLGNUMMER,
            EVENEMENT_ID = excluded.EVENEMENT_ID
        ''', (wisselpunt_id, wisselpunt_naam, etappe_volgnummer, evenement_id))

def get_wisselpunten(evenement_id):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute('''
            SELECT WISSELPUNT_NAAM, ETAPPE_VOLGNUMMER
            FROM WISSELPUNTEN
            WHERE EVENEMENT_ID = ?
            ORDER BY ETAPPE_VOLGNUMMER
        ''', (evenement_id,))

        rows = cursor.fetchall()

        return {
            "ETAPPE_NAAM_list": [row["WISSELPUNT_NAAM"] for row in rows],
            "ETAPPE_VOLGNUMMER_list": [row["ETAPPE_VOLGNUMMER"] for row in rows]
        }

def get_wisselpunt_by_etappe(evenement_id, etappe_volgnummer):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.execute('''
            SELECT WISSELPUNT_NAAM
            FROM WISSELPUNTEN
            WHERE EVENEMENT_ID = ?
            AND ETAPPE_VOLGNUMMER = ?
        ''', (evenement_id, etappe_volgnummer))

        row = cursor.fetchone()

    if row is not None:
        return row[0]

    return None

def insert_ploeg(ploeg_id, ploegnummer, ploeg_naam, evenement_id):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('''
          INSERT INTO PLOEGLIJST (PLOEG_ID, PLOEGNUMMER, PLOEG_NAAM, EVENEMENT_ID)
          VALUES (?, ?, ?, ?)
          ON CONFLICT(PLOEG_ID) DO UPDATE SET
            PLOEGNUMMER = excluded.PLOEGNUMMER,
            PLOEG_NAAM = excluded.PLOEG_NAAM,
            EVENEMENT_ID = excluded.EVENEMENT_ID
        ''', (ploeg_id, ploegnummer, ploeg_naam, evenement_id))

def get_ploeglijst(evenement_id):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute('''
            SELECT PLOEGNUMMER, PLOEG_NAAM
            FROM PLOEGLIJST
            WHERE EVENEMENT_ID = ?
            ORDER BY PLOEGNUMMER
        ''', (evenement_id,))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

def insert_evenement(evenement_id, evenement_naam):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('''
          INSERT INTO EVENEMENTEN (EVENEMENT_ID, EVENEMENT_NAAM)
          VALUES (?, ?)
          ON CONFLICT(EVENEMENT_ID) DO UPDATE SET
            EVENEMENT_NAAM = excluded.EVENEMENT_NAAM
        ''', (evenement_id, evenement_naam))

def insert_instelling(instelling_naam, instelling_waarde):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute('''
          INSERT INTO INSTELLINGEN (INSTELLING_NAAM, INSTELLING_WAARDE)
          VALUES (?, ?)
          ON CONFLICT(INSTELLING_NAAM) DO UPDATE SET
            INSTELLING_WAARDE = excluded.INSTELLING_WAARDE
        ''', (instelling_naam, instelling_waarde))

def get_instelling(instelling_naam):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        cursor = conn.execute('''
            SELECT INSTELLING_WAARDE
            FROM INSTELLINGEN
            WHERE INSTELLING_NAAM = ?
        ''', (instelling_naam,))

        row = cursor.fetchone()

        if row is not None:
            return row[0]

        return None

def get_missende_ploegen(evenement_id, etappe_volgnummer):
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row

        cursor = conn.execute('''
            SELECT
                PLOEGLIJST.PLOEGNUMMER,
                PLOEGLIJST.PLOEG_NAAM
            FROM PLOEGLIJST
            LEFT JOIN DOORKOMSTEN
                ON PLOEGLIJST.PLOEGNUMMER = DOORKOMSTEN.PLOEG
                AND DOORKOMSTEN.EVENEMENT_ID = PLOEGLIJST.EVENEMENT_ID
                AND DOORKOMSTEN.ETAPPE_VOLGNUMMER = ?
            WHERE PLOEGLIJST.EVENEMENT_ID = ?
              AND DOORKOMSTEN.PLOEG IS NULL
            ORDER BY PLOEGLIJST.PLOEGNUMMER
        ''', (etappe_volgnummer, evenement_id))

        return [dict(row) for row in cursor.fetchall()]

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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

        for table_name in tables:
            rows = cur.execute(f"SELECT * FROM {table_name}").fetchall()
            columns = [col[1] for col in cur.execute(f"PRAGMA table_info({table_name})")]

            csv_path = output_dir / f"{timestamp}_{table_name.lower()}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(columns)
                writer.writerows(rows)

            print(f"Exported {table_name} -> {csv_path}")
    finally:
        conn.close()

if __name__ == "__main__":
#    print_schema()
    clear_doorkomsten()
    export_all_tables_to_csv()
#    print(get_missende_ploegen(4, 12))

    
