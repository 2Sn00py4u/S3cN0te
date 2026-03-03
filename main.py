import json, util.fileUtil as fileUtil
from flask import Flask, render_template, url_for, jsonify, request, redirect,  session
import datetime, os
from flask_session import Session
import pathlib as plib
import util.duck_dbms as duck
import util.duck_functions as duck_func
from util.crypting import Cryptor
import string
import secrets
import base64 as b64

CONFIGPATH = plib.Path("config.json")
DBPATH = plib.Path("data/s3cn0te.duckdb")
OUTPATH = plib.Path("downloads")
HOST = "localhost"
PORT = 55555


def getConfig(configPath: plib.Path) -> None:
    """
    Vor.: Ein valider Pfad zu der entsprechenden config.json-Datei
    Eff.: --
    Erg.: Die globalen Konfigurationsvariablen werden gesetzt
    """
    global DBPATH, OUTPATH, HOST, PORT
    with open(configPath, "r") as file:
        config = json.loads(file.read())
        file.close()
    DBPATH = plib.Path(config["dbpath"])
    OUTPATH = plib.Path(config["outpath"])
    HOST = config["host"]
    PORT = config["port"]
    
def printBanner() -> None:
    """
    Vor.: --
    Eff.: --
    Erg.: Das Logo/Banner wird in der Konsole geschrieben + alle Konfigurationen
    """
    BLUE = "\033[34m"
    CYAN = "\033[36m"

    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(fr"""{CYAN}{BOLD}
         ____             _   _       _                
        / ___|  ___  ___ | \ | | ___ | |_ ___      
        \___ \ / _ \/ __/|  \| |/ _ \| __/ _ \  
         ___) |  __/  (_ | |\  | (_) | ||  __/ 
        |____/ \___|\___\|_| \_|\___/ \__\___|
    {RESET}""")
    print(f"{BLUE}{BOLD}[*] S3cN0te - Config: '{CONFIGPATH.absolute()}'{RESET}")
    print(f"{BLUE}{BOLD}[*] DBPATH: '{DBPATH.absolute()}'{RESET}")
    print(f"{BLUE}{BOLD}[*] OUTPATH: '{OUTPATH.absolute()}'{RESET}")
    print(f"{BLUE}{BOLD}[*] HOST: '{HOST}'{RESET}")
    print(f"{BLUE}{BOLD}[*] PORT: '{PORT}'{RESET}")  
        
def get_random_string(length: int = 20) -> str:
    """
    Vor.: Die Länge des zufallsgenerierten Strings
    Eff.: --
    Erg.: Ein zufällig generierter String der Länge -length-
    """
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def checkValidRegex(string: str) -> bool:
    """
    Vor.: Der zu untersuchende String -string-
    Eff.: --
    Erg.: Liefert einen Wahrheitswert, ob nur erlaubte Zeichen verwendet wurden
    """
    allowed_alpha = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "ä", "ö", "ü"]
    allowed_caps = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ä', 'Ö', 'Ü']
    allowed_chars = ["-", ".", "_", "#", "@"]
    allowed_nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    for letter in string:
        if letter not in allowed_alpha and letter not in allowed_caps and letter not in allowed_chars and letter not in allowed_nums:
            print(f"unallowed char: {letter}")
            return False
    return True

class API:
    """
    Vor.: Notwendige Parameter: -dbms- ist ein Objekt der Klasse duck.DBMS für die Datenbankverwaltung
          Optionale Parameter: 
                Datentyp 'str' | 'plib.Path':   -host- IPadresse zum bereitstellen der API
                                                -session_type- Form der Sessionspeicherung Festplatte/Arbeitsspeicher
                                                -session_file_dir- Speicherort der auf der Festplatten gespeicherten Sessions
                Datentyp 'int':
                                                -port- Ist der Port/Kanal zum bereitstellen der API
                                                -session_file_threshold- ist die maximale Anzahl an Sessiondateien in dem Speicherpfad
                Datentyp 'bool':
                                                -session_permanent- Wahrheitsausage ob die erstellte Session eines Benutzers permanent ist
                                                -session_use_signer- Wahrheitsausage ob die API-Sessions signiert werden für jeden Benutzer
                                                -debug- Wahrheitsausage ob weiterer Output angezeigt werden soll
                Andere Datentypen:
                                                -permanent_session_lifetime- Lebensdauer einer Session vom Datentyp: datetime.timedelta    
    Eff.: Ein Objekt der Klasse "API" mit den vorausgesetzten Attributen wird im Speicher initialisiert 
    Erg.: Ein Objekt der Klasse "API"
    """
    def __init__(self, dbms: duck.DBMS, host: str = "localhost", port: int = 55555, session_type: str = "filesystem", session_file_dir: str|plib.Path = plib.Path("sessions"), session_file_threshold: int = 500,
                 session_permanent: bool = True, session_use_signer: bool = True, permanent_session_lifetime: datetime.timedelta = datetime.timedelta(minutes=5), debug: bool = False) -> "API":
        self.flaskapi: Flask = Flask(__name__)
        self.dbms: duck.DBMS = dbms
        self.cryptor: Cryptor = Cryptor()
        self.host: str = host
        self.port: int = port
        self.__secnote_content: list = []
        
        self.session: Session = None
        self.__session_config: dict = {
            "SESSION_TYPE": session_type,
            "SESSION_FILE_DIR": session_file_dir,
            "SESSION_FILE_THRESHOLD": session_file_threshold,
            "SESSION_PERMANENT": session_permanent,
            "SESSION_USE_SIGNER": session_use_signer,
            "PERMANENT_SESSION_LIFETIME": permanent_session_lifetime
        }
        self.__session_secret_key: str = None
        self.__session_configured: bool = False
        self.__API_initialized: bool = False
        self.__API_running: bool = False
        
        self.debug = debug
        
    def get_status(self) -> dict:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt den Status der API als -dict- wieder
        """
        return {
            "session_configured": self.__session_configured,
            "API_initialized": self.__API_initialized,
            "API_running": self.__API_running
        }
        
    def get_session_config(self) -> dict:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt die Konfiguierung des Session-Managements wieder
        """
        return self.__session_config
    
    def set_session_config(self, session_config: dict) -> None:
        """
        Vor.: Eine valide Konfigartion als Datentyp: dict
        Eff.: Das Session-Management des Objekts wird angepasst
        Erg.: Ein verändertes Session-Management der API
        """
        self.__session_config = session_config
    
    def get_session_secret_key(self) -> str:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt den Session-Secret-Key wieder
        """
        return self.__session_secret_key
    
    def configSession(self, session_secret_key: str) -> None:
        """
        Vor.: Ein valider Session-Schlüssel als string
        Eff.: Setzen von lokalen Variablen des Objekts zur Konfiguration des Session-Managements
        Erg.: --
        """
        try:
            self.flaskapi.config.from_mapping(self.get_session_config())
            self.session = Session(self.flaskapi)
            self.flaskapi.secret_key = session_secret_key
            self.__session_configured = True
            
        except Exception as e:
            raise Exception(f"[!] Error while sessionconfig: {e}")
    
    def initAPI(self) -> None:
        """
        Vor.: --
        Eff.: Initialisierung der API mit allen Endpoints und den entsprechenden Operationen
        Erg.: --
        """
        @self.flaskapi.route("/")
        @self.flaskapi.route("/home")
        def home():
            """
            Vor.: --
            Eff.: --
            Erg.: Gibt die Startpage im angemeldeten Zustand wieder
            """
            if not "user" in session and not "alive" in session:
                return redirect(url_for("login"))
            else:
                return render_template("home.html", title= "home")
        
        @self.flaskapi.route("/login", methods=['POST', 'GET'])
        def login():
            """
            Vor.: --
            Eff.: --
            Erg.: Gibt die Anmeldeseite wieder
            """
            if not "user" in session and not "alive" in session:
                match request.method:
                    case "GET":
                        return render_template("login.html", title= "login")
                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            username = data["username"]
                            password = data["password"]
                            if not checkValidRegex(username) or not checkValidRegex(password):
                                return jsonify({"status": "success", "valid": False}), 200
                            
                            if duck_func.Log1n(self.dbms, username, password):
                                session.permanent = True
                                session["alive"] = True
                                session["user"] = username
                                session["key"] = get_random_string()
                                session["pass"] = b64.encodebytes(self.cryptor.encrypting(password, session["key"]))
                                return jsonify({"status": "success", "valid": True}), 200
                            else:
                                return jsonify({"status": "success", "valid": False}), 200
                        
                        except Exception as e:
                            print(f"[!] Error @login()_POST: {e}")
                            return jsonify({"error": str(e)}), 500
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("home"))
            
        @self.flaskapi.route("/register", methods=['POST', 'GET'])
        def register():
            """
            Vor.: --
            Eff.: --
            Erg.: Gibt die Registrierungs-Seite wieder
            """
            if not "user" in session and not "alive" in session:
                match request.method:
                    case "GET":
                        return render_template("register.html", title= "register")
                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            username = data["username"]
                            password = data["password"]
                            if not checkValidRegex(username) or not checkValidRegex(password):
                                return jsonify({"status": "success", "valid": False}), 200
                            
                            if duck_func.R3gister(self.dbms, username, password):
                                session.permanent = True
                                session["alive"] = True
                                session["user"] = username
                                session["key"] = get_random_string()
                                session["pass"] = b64.encodebytes(self.cryptor.encrypting(password, session["key"]))
                                return jsonify({"status": "success", "valid": True}), 200
                            else:
                                return jsonify({"status": "success", "valid": False}), 200
                        
                        except Exception as e:
                            print(f"[!] Error @register()_POST: {e}")
                            return jsonify({"error": str(e)}), 500
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("home"))
              
        @self.flaskapi.route("/user", methods=['GET'])
        def user_profile():
            """
            Vor.: --
            Eff.: --
            Erg.: Gibt die Benutzerprofil-Seite wieder
            """
            if "user" in session and "alive" in session:
                username = session["user"]
                password = self.cryptor.decrypting(b64.decodebytes(session["pass"]), session["key"])
                return render_template("user.html", username = username, password = password)
            else:
                return redirect(url_for("login"))
         
        @self.flaskapi.route("/user/edit", methods=['POST'])
        def user_edit():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zur Veränderung des Benutzerprofils dar
            """
            if "user" in session and "alive" in session:
                if request.method == "POST":
                    try:
                        data = request.json
                        username = session["user"]
                        new_username = data["new_username"]
                        new_password = data["new_password"]
                        if not checkValidRegex(username) or not checkValidRegex(new_username) or not checkValidRegex(new_password):
                            return jsonify({"status": "success", "valid": False}), 200
                            
                        if duck_func.updateLogin(self.dbms, username, new_username, new_password):
                            session.pop('user', None)
                            session.pop('alive', None)
                            session.pop('key', None)
                            session.pop('pass', None)
                            return jsonify({"status": "success", "valid": True}), 200
                        return jsonify({"status": "success", "valid": False}), 200
                    
                    except Exception as e:
                        return jsonify({"error": str(e)}), 500
                    
        @self.flaskapi.route("/user/delete", methods=['GET'])
        def user_delete():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zur Löschung des Benutzers dar
            """
            if "user" in session and "alive" in session:
                username = session["user"]
                try:
                    duck_func.deleteUser(self.dbms, username)
                    session.pop('user', None)
                    session.pop('alive', None)
                    session.pop('key', None)
                    session.pop('pass', None)
                except Exception as e:
                    print(f"[!] Error deleting User '{username}': {e}")
                    return redirect(url_for("home"))
                return redirect(url_for("register"))
            else:
                return redirect(url_for("login"))
        
        @self.flaskapi.route("/edit/new", methods=['GET', 'POST'])
        def newfile_edit():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zur Bearbeitung einer neuen SecNote dar.
            """
            if "user" in session and "alive" in session:
                match request.method:
                    case "GET":
                        return render_template("edit.html", title= "edit")
                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            req = data["req"]
                            if req == "edit?":
                                return jsonify({"status": "success", "edit": "new", "pages": [{"id": "0", "markdown": "# New\n"}]}), 200

                        except Exception as e:
                            print(f"[!] Error @edit/new()_POST: {e}")
                            return jsonify({"error": str(e)}), 500
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("login"))
            
        @self.flaskapi.route("/edit/open", methods=['GET', 'POST'])
        def openfile_edit():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zur Bearbeitung einer bereits vorhandenen SecNote dar
            """
            if "user" in session and "alive" in session:
                match request.method:
                    case "GET":
                        return render_template("edit.html", title= "edit")
                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            req = data["req"]
                            if req == "edit?":
                                return jsonify({"status": "success", "edit": "new", "pages": self.__secnote_content}), 200

                        except Exception as e:
                            print(f"[!] Error @edit/new()_POST: {e}")
                            return jsonify({"error": str(e)}), 500
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("login"))
        
        @self.flaskapi.route("/edit/save", methods=['POST'])
        def savefile():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zum Speichern einer SecNote dar
            """
            if "user" in session and "alive" in session:
                match request.method:                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            
                            pages_list = data["pages_list"]
                            secnote = fileUtil.SecNote(plib.Path(f"{OUTPATH}/{data['name']}.secnote"), pages_list, data["key"])
                            if secnote.save():
                                return jsonify({"status": "success", "valid": True, "path": str(secnote.get_path().absolute())}), 200
                            return jsonify({"error": "couldn't save secnote"}), 500

                        except Exception as e:
                            print(f"[!] Error @edit/save()_POST: {e}")
                            return jsonify({"error": str(e)}), 500
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("login"))
        
        @self.flaskapi.route("/edit/convert", methods=['POST'])
        def convertfile():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zum Konvertieren einer SecNote in das Dateiformat .png/.pdf dar
            """
            if "user" in session and "alive" in session:
                match request.method:                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            con_format = data["format"]
                            match con_format:
                                case ".png":
                                    secnote = fileUtil.SecImage(plib.Path(f"{OUTPATH}/secimg_{datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")}.png"), data["content"])
                                    if secnote.save():
                                        return jsonify({"status": "success", "valid": True, "path": str(secnote.get_path().absolute())}), 200
                                    else:
                                        return jsonify({"status": "success", "valid": False}), 200
                                case ".pdf":
                                    pages_list = data["pages_list"]
                                    html_content = []
                                    for page in pages_list:
                                        html_content.append(page["html"])
                                    secnote = fileUtil.SecPDF(plib.Path(f"{OUTPATH}/secpdf_{datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")}.pdf"), html_content)
                                    if secnote.save():
                                        return jsonify({"status": "success", "valid": True, "path": str(secnote.get_path().absolute())}), 200
                                    else:
                                        return jsonify({"status": "success", "valid": False}), 200
                                case _:
                                    return jsonify({"error": "couldn't save secnote"}), 500
                                    
                            return jsonify({"error": "couldn't save secnote"}), 500

                        except Exception as e:
                            print(f"[!] Error @edit/convert()_POST: {e}")
                            return jsonify({"error": str(e)}), 500
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("login"))
        
        @self.flaskapi.route("/open", methods=['POST'])
        def openfile():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zum Öffnen und Einlesen einer SecNote dar
            """
            if "user" in session and "alive" in session:
                match request.method:                    
                    case "POST":
                        try:
                            data = request.json
                            if data is None:
                                raise ValueError("No JSON data received")
                            
                            path = plib.Path(data["path"])
                            key = data["key"]
                            secnote = fileUtil.SecNote(path, {}, key)
                            self.__secnote_content = secnote.read()
                            if not self.__secnote_content:
                                return jsonify({"status": "success", "valid": False, "error": str(e)}), 200
                            return jsonify({"status": "success", "valid": True, "href": "/edit/open"}), 200

                        except Exception as e:
                            print(f"[!] Error @edit/open()_POST: {e}")
                            return jsonify({"status": "success", "valid": False, "error": str(e)}), 200
                    
                    case _:
                        print(f"[!] wrong method: {request.method}")
                        return jsonify({"error": "Method not allowed"}), 405
            else:
                return redirect(url_for("login"))
        
        @self.flaskapi.route("/logout", methods=['GET'])
        def logout():
            """
            Vor.: --
            Eff.: --
            Erg.: Stellt den Endpunkt zum Abmeldeneines Benutzers dar
            """
            if 'user' in session and 'alive' in session:
                session.pop('user', None)
                session.pop('alive', None)
                session.pop('key', None)
                session.pop('pass', None)
                return redirect(url_for("login"))
            else:
                return redirect(url_for("login"))
            
        self.__API_initialized = True
    
    def run(self) -> None:
        """
        Vor.: --
        Eff.: --
        Erg.: Startet den Host-Vorgang der API, wenn sie entsprechend vorbereitet ist
        """
        status = self.get_status()
        if status["API_running"]:
            print("[!] API is allready running.")

        if status["session_configured"] and status["API_initialized"]:
            self.__API_running = True
            self.flaskapi.run(host = self.host, port = self.port, debug = self.debug)

        else:
            raise Exception("[!] API and/or Session wasn't initialized/configured.")
     
if __name__ == "__main__":
    getConfig(CONFIGPATH)
    
    if not OUTPATH.exists():
        os.makedirs(OUTPATH)
        
    if not DBPATH.exists():
        secnoteDBMS = duck_func.build_S3cN0te_DB(DBPATH)
    else:
        secnoteDBMS = duck_func.connect_S3cN0te_DB(DBPATH)
    
    printBanner()    
    secnoteAPI = API(secnoteDBMS, HOST, PORT)
    secnoteAPI.configSession("sessionSecret1234")
    secnoteAPI.initAPI()
    secnoteAPI.run()