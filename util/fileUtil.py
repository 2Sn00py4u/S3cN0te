import pathlib as plib
import json, os
try:
    from util.crypting import Cryptor
except ImportError:
    from crypting import Cryptor
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter

class SecFile:
    """
    Vor.: Der Speicherpfad -path- als plib.Path, der Inhalt -content- als list oder str
    Eff.: Ein Objekt der Klasse SecFile wird im RAM initialisiert
    Erg.: Ein Objekt der Klasse SecFile
    """
    def __init__(self, path: plib.Path, content: list | str) -> "SecFile":
        self.__path: plib.Path = path
        self.__content: list | str = content
    
    def get_path(self) -> plib.Path:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt den Speicherpfad wieder
        """
        return self.__path
    
    def get_content(self) -> list | str:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt den Inhalt wieder
        """
        return self.__content
    
    def set_path(self, path: plib.Path) -> None:
        """
        Vor.: Ein valider Speicherpfad als plib.Path
        Eff.: Setzt die Objektvariable des Speicherpfades
        Erg.: --
        """
        if path.exists():
            self.__path = path
            
    def set_content(self, content: list | str) -> None:
        """
        Vor.: Ein valider Inhalt als list oder str
        Eff.: Setzt die Objektvariable des Inhalts
        Erg.: --
        """
        self.__content = content
    
class SecNote(SecFile):
    """
    Vor.: 
        -path- ist der Speicherordner als Datentyp: plib.Path
        -content- ist der Inhalt der .secnote Datei als Datentyp: dict
        -encryption_key- ist der Verschlüsselungs-Schlüssel als Datentyp: str
        Die Klasse SecFile als Elternklasse
    Eff.: Ein Objekt der Klasse "SecNote" mit den vorausgesetzten Attriburten wird im Arbeitsspeicher initialisiert
    Erg.: Ein Objekt der Klasse "SecNote"
    """
    def __init__(self, path: plib.Path, content: dict, encryption_key: str) -> "SecNote":
        SecFile.__init__(self, path, content)
        self.__path = self.get_path()
        self.__content = self.get_content()
        self.__encryption_key: str = encryption_key
        self.__cryptor: Cryptor = Cryptor()
    
    def get_encryptionKey(self) -> str:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt den Verschlüsselungs-Schlüssel wieder
        """
        return self.__encryption_key
    
    def set_encryptionKey(self, new_key: str) -> None:
        """
        Vor.: Einen Schlüssel -new_key- als str
        Eff.: Die Objektvariable des Verschlüsselungs-Schlüssels wird gesetzt
        Erg.: --
        """
        self.__encryption_key = new_key
        
    def save(self) -> bool:
        """
        Vor.: --
        Eff.: Speicher den Inhalt sicher als .secnote Datei
        Erg.: Gibt eine Wahrheitsaussage darüber, ob die Datei verschlüsselt gespeichert wurde wieder
        """
        try:
            with open(self.__path, "wb") as file:
                file.write(self.__cryptor.encrypting(json.dumps(self.__content), self.__encryption_key))
                file.close()
            return True
        except Exception as e:
            print(e)
            return False
        
    def read(self) -> list | dict | bool:
        """
        Vor.: --
        Eff.: --
        Erg.: Gibt entweder den Inhalt einer .secnote-Datei als list, dict wieder, oder False wenn die Datei nicht gelesen werden konnte
        """
        try:
            with open(self.__path, "rb") as file:
                content = json.loads(self.__cryptor.decrypting(file.read(), self.__encryption_key))
                file.close()
            return content
        except Exception as e:
            print(e)
            return False

def generateTemplate(sec_content: str, title: str) -> str:
    """
    Vor.: Inhalt als str in HTML-Syntax, den Titel als str
    Eff.: --
    Erg.: Wiedergabe eines Templates für die Speicherung als PDF und PNG in str-Format
    """
    html_content = f"""
<!DOCTYPE html>
<html>
    <head>
    <meta charset="utf-8">
    <title>{title}</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        html, body {{
            height: 100%;
            width: 100%;
            background-color: #212529;
        }}
        
        #content {{
            aspect-ratio: 16 / 9;
            width: 100%;
            max-width: 1920px;
            height: 100%;
            flex-shrink: 0;
            color: #fffcf8; 
            background-color: #212529; 
            padding: 2rem; 
            border-radius: 10px;
            font-family: system-ui, sans-serif;
            font-size: 18px;
            line-height: 1.4em;
            overflow: hidden;
            white-space: pre-wrap;
            word-break: break-word;
        }}
    </style>
    </head>
    <body style="background-color: #212529;">
        <div style="display: flex; justify-content: center; height: 100vh; width: 105vh;">
            <div id="content">
                {sec_content}
            </div>
        </div>
    </body>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</html>
"""
    return html_content

class SecImage(SecFile):
    """
    Vor.: 
        -path- ist der Speicherordner als Datentyp: plib.Path
        -content- ist der Inhalt der .secnote Datei als Datentyp: str
        Die Klasse SecFile als Elternklasse
    Eff.: Ein Objekt der Klasse "SecImage" mit den vorausgesetzten Attriburten wird im Arbeitsspeicher initialisiert
    Erg.: Ein Objekt der Klasse "SecImage"
    """
    def __init__(self, path: plib.Path, content: str) -> "SecImage":
        SecFile.__init__(self, path, content)
        self.__content: str = self.get_content()
        self.__path: plib.Path = self.get_path()
        self.__html_content = generateTemplate(self.__content, str(self.__path.name))
        
    def save(self) -> bool:
        """
        Vor.: --
        Eff.: Speichern des HTML-Inhalts als Bild im .png-Format
        Erg.: Wahrheitsaussage, ob das Bild gespeichert wurde
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                page.set_content(self.__html_content, wait_until="networkidle")
                page.screenshot(
                    path=self.__path.absolute(),
                    full_page=True,
                    type="png"
                )

                browser.close()
            return True
        except:
            return False
            
class SecPDF(SecFile):
    """
    Vor.: 
        -path- ist der Speicherordner als Datentyp: plib.Path
        -content- ist der Inhalt der .secnote Datei als Datentyp: dict
        Die Klasse SecFile als Elternklasse
    Eff.: Ein Objekt der Klasse "SecNote" mit den vorausgesetzten Attriburten wird im Arbeitsspeicher initialisiert
    Erg.: Ein Objekt der Klasse "SecNote"
    """
    def __init__(self, path: plib.Path, content: list, tmp: plib.Path = plib.Path("tmp")) -> "SecPDF":
        SecFile.__init__(self, path, content)
        self.__content: list = self.get_content()
        self.__path: plib.Path = self.get_path()
        self.__tmp = tmp
          
    def save(self) -> bool:
        """
        Vor.: --
        Eff.: Speichern des HTML-Inhalts als PDF-Datei
        Erg.: Wahrheitsaussage, ob die PDF-Datei gespeichert wurde
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                for i, con in enumerate(self.__content):
                    page = browser.new_page(viewport={"width": 1920, "height": 1080})
                    page.set_content(generateTemplate(con, str(self.__path.name)), wait_until="networkidle")
                    page.pdf(
                        path=self.__tmp.joinpath(f"part{i}_{self.__path.name}.pdf"),
                        width="1920px",
                        height="1080px",
                        scale=1,
                        print_background=True,
                        prefer_css_page_size=False,
                        margin={"top": "0cm", "bottom": "0cm", "left": "0cm", "right": "0cm"}
                    )
                browser.close()
    
            pdf_files = sorted(self.__tmp.glob(f"*{self.__path.name}.pdf"))
            merger = PdfWriter()
            for pdf in pdf_files:
                merger.append(pdf)
            merger.write(self.__path)
            merger.close()
            
            for pdf in pdf_files:
                os.remove(pdf)
                
            return True
        except:
            return False
