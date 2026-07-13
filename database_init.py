import sqlite3


# sql code nog loskoppelen van de rest van de code, zodat het makkelijker is om de database te wijzigen
with sqlite3.connect("Veluweloop_DB") as conn:
    # maken van de tabel voor de doorkomsten
    # besluiten of de registraties van andere wisselpunten vanuit de remote databasde ook in deze tabel komen
    conn.execute('''
      CREATE TABLE IF NOT EXISTS DOORKOMSTEN(
      ID_LOCAL INTEGER PRIMARY KEY,
      ID_SERVER INTEGER,
      DATETIME TEXT NOT NULL,
      PLOEG INTEGER NOT NULL,
      ID_LOCATIE INTEGER NOT NULL,
      STATUS TEXT NOT NULL
      )
    ''')
  
    conn.execute('''
      CREATE TABLE IF NOT EXISTS WISSELPUNTEN(
      ID INTEGER PRIMAIRE KEY,
      NAAM TEXT NOT NULL,
      ETAPPE_VOLGNUMMER INTEGER NOT NULL
      )
  ''')

    conn.execute('''             
      CREATE TABLE IF NOT EXISTS PLOEGLIJST(
      PLOEG_ID INTEGER PRIMAIRE KEY,
      PLOEGNUMMER INTEGER NOT NULL,
      NAAM TEXT NOT NULL
      )
  ''')

