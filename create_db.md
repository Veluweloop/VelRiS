CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE checkpointteam(id INTEGER PRIMARY KEY AUTOINCREMENT, checkpointteam_name TEXT);
CREATE TABLE checkpoint (id INTEGER PRIMARY KEY AUTOINCREMENT, checkpoint_name TEXT);
CREATE TABLE doorkomst (id INTEGER PRIMARY KEY AUTOINCREMENT, tijd TEXT, ploeg TEXT, type TEXT, wisselpunt TEXT, wisselpuntploeg TEXT, serialid TEXT, sync TEXT);
CREATE TABLE transponder (id INTEGER PRIMARY KEY AUTOINCREMENT, tagid TEXT, ploeg TEXT);
CREATE TABLE instellingen (id INTEGER PRIMARY KEY AUTOINCREMENT, serialid TEXT, wisselpuntploeg TEXT, wisselpunt TEXT);
