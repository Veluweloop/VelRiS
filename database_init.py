import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("Veluweloop_DB")

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
          STATUS TEXT NOT NULL
          )
        ''')

        conn.execute('''
          CREATE TABLE IF NOT EXISTS WISSELPUNTEN(
          ID INTEGER NOT NULL PRIMARY KEY,
          WISSELPUNT_NAAM TEXT NOT NULL,
          ETAPPE_VOLGNUMMER INTEGER NOT NULL
          )
      ''')

        conn.execute('''             
          CREATE TABLE IF NOT EXISTS PLOEGLIJST(
          PLOEG_ID INTEGER NOT NULL PRIMARY KEY,
          PLOEGNUMMER INTEGER NOT NULL,
          PLOEG_NAAM TEXT NOT NULL
          )
      ''')

        conn.execute('''             
          CREATE TABLE IF NOT EXISTS EVENEMENTEN(
          EVENEMENT_ID INTEGER NOT NULL PRIMARY KEY,
          EVENEMENT_NAAM TEXT NOT NULL
          )
      ''')

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
    
if __name__ == "__main__":
    print_schema()

