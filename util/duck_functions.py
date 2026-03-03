try:
    import util.duck_dbms as db
    import util.crypting as cy
except ImportError:
    import duck_dbms as db
    import crypting as cy   
import base64 as b64
import pathlib as plib

Cryptor = cy.Cryptor()
def connect_S3cN0te_DB(filePath: str) -> db.DBMS:
    """
    Vor.: --
    Eff.: --
    Erg.: Verbindung zur DB wird aufgebaut und zurückgegeben
    """
    return db.DBMS(filePath)

def build_S3cN0te_DB(filePath: str) -> db.DBMS:
    # Funktion primär zum neu-aufsetzen der Datenbank mit Testwerten (debuggen)
    """
    Vor.: --
    Eff.: Zum entsprechenden Dateipfad wird eine neue Datenbank-Datei erstellt
    Erg.: Datenbank mit Testwerten
    """
    S3cN0te_DBMS = db.DBMS(filePath)
    tables = S3cN0te_DBMS.getTables()
    for table in tables:
        try:
            S3cN0te_DBMS.deleteTable(table)
        except:
            pass
       
    # users(_uname_, passwd)
    S3cN0te_DBMS.createTable("users",["username VARCHAR PRIMARY KEY NOT NULL", "password BLOB"])
    R3gister(S3cN0te_DBMS, "admin", "admin")
    return S3cN0te_DBMS

def Log1n(DBMS: db.DBMS, username: str, password: str) -> bool:
    """
    Vor.: Verbindung zur Datenbank, Benutzername und Passwort sind bekannt
    Eff.: Simple Datenbankabfrage, ob der Benutzername und das Passwort korrekt sind
    Erg.: Login-Status wird zurückgegeben
    """
    S3cN0te_DBMS = DBMS
    valid = False
    result = S3cN0te_DBMS.execute(f"""SELECT * FROM users WHERE username = ?""", False, username)
    if result != []:
        userpassword = b64.decodebytes(S3cN0te_DBMS.execute(f"""SELECT password FROM users WHERE username = ?""", False, username)[0][0])
        valid = Cryptor.compare_encrypted(password, password, userpassword)
    return valid
    
    
def R3gister(DBMS: db.DBMS, username: str, password: str) -> bool:
    """
    Vor.: Verbindung zur Datenbank, Benutzername und Passwort sind bekannt
    Eff.: Simple Datenbankabfrage, ob der Benutzername und das Passwort korrekt bzw. unbenutzt sind
    Erg.: Registrier-Status wird zurückgegeben
    """
    S3cN0te_DBMS = DBMS
    try:
        S3cN0te_DBMS.insertValues("users",[(username, b64.encodebytes(Cryptor.encrypting(password, password)))])
        r3gistert = True
    except Exception as e:
        r3gistert = False
    return r3gistert

def updateLogin(DBMS: db.DBMS, username: str, new_username: str, password: str) -> bool:
    """
    Vor.: Verbindung zur Datenbank, Benutzername, neuer Benutzername und neues Passwort sind bekannt
    Eff.: Die verschlüsselten Login-Daten des Benutzers werden aktualisiert
    Erg.: Update-Status wird zurückgegeben
    """
    S3cN0te_DBMS = DBMS
    result = S3cN0te_DBMS.execute(f"""SELECT * FROM users WHERE username = ?""", False, new_username)
    if result == [] or new_username == username:
        try:
            S3cN0te_DBMS.execute(f"""UPDATE users SET password = ? WHERE username = ?""", False, b64.encodebytes(Cryptor.encrypting(password, password)), username)
            S3cN0te_DBMS.execute(f"""UPDATE users SET username = ? WHERE username = ?""", False, new_username, username)
            return True
        except Exception as e:
            return False
    return False

def deleteUser(DBMS: db.DBMS, username: str):
    """
    Vor.: Verbindung zur Datenbank und Benutzername sind bekannt
    Eff.: Der Eintrag eines Benutzer in der Benutzerdatenbank wird gelöscht
    Erg.: Lösch-Status wird zurückgegeben
    """
    S3cN0te_DBMS = DBMS
    try:
        DBMS.execute("""DELETE FROM users WHERE username = ?""", False, username)
        return True
    except:
        return False

def closeConnection(DBMS: db.DBMS) -> None:
    """
    Vor.: --
    Eff.: --
    Erg.: Verbindung zur DB wird geschlossen
    """
    DBMS.disconnectDB()

def testDBfunc():    
    DBPATH = plib.Path("data/S3cN0te.duckdb")
    if not DBPATH.exists():
        dbms = build_S3cN0te_DB(DBPATH)
    else:
        dbms = connect_S3cN0te_DB(DBPATH)
    print(dbms.execute(f"""SELECT * FROM users""", True))
    '''print(Log1n(dbms, "admin", "password"))
    print(updateLogin(dbms, "admin", "user", "user"))
    print(dbms.execute(f"""SELECT * FROM users""", True))
    print(Log1n(dbms, "user", "user"))
    print(deleteUser(dbms, "user"))
    print(Log1n(dbms, "user", "user"))'''
    closeConnection(dbms)
#testDBfunc()