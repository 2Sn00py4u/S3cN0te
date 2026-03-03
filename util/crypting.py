from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Cryptor:
    """
    Vor.: keine erzwingenden
    Eff.: Ein Objekt der Klasse Cryptor wird im Arbeitsspeicher initialisiert
    Erg.: Ein Objekt der Klasse Cryptor
    """
    def __init__(self, blockdecryption: str = "ECB", encoding: str = "utf-8"):
        self.blockdecryption = blockdecryption
        self.encoding = encoding
        
    def encrypting(self, password: str, key: str) -> bytes:
        """
        Vor.: Verschlüsselungsschlüssel und Passwort sind bekannt
        Eff.: Das 'gepaddete' Passwort wird mit Hilfe des AES-Algorithmus und des Schlüssels verschlüsselt
        Erg.: Verschlüsseltes Passwort wird als Byte-Objekt zurückgegeben
        """         
        byte_password = bytes(password, self.encoding)
        byte_key = bytes(key, self.encoding)
        encryption_key = pad(byte_key, AES.block_size)
        
        if self.blockdecryption == "ECB":
            try:
                cipher = AES.new(encryption_key, AES.MODE_ECB)
            except Exception as e:
                raise Exception(f"an error accured, make shure, to use the right key\nerror:{e}")
        else:
            raise Exception("other than ECB not done yet...")
        
        try:
            padded_password = pad(byte_password, AES.block_size)
            encrypted_password = cipher.encrypt(padded_password)
            return encrypted_password
        except:
            raise Exception(f"error encrypting {byte_password}") 
    
            
    def decrypting(self, encrypted_bytes:bytes, key:str) -> str:
        """
        Vor.: Verschlüsselungsschlüssel und verschlüsseltes Passwort sind bekannt
        Eff.: Die verschlüsselten Bytes werden mit Hilfe des AES-Algorithmus und des Schlüssels entschlüsselt
        Erg.: Entschlüsseltes Passwort wird als String-Objekt zurückgegeben
        """
        byte_key = bytes(key, self.encoding)
        encryption_key = pad(byte_key, AES.block_size)
        
        if self.blockdecryption == "ECB":
            try:
                cipher = AES.new(encryption_key, AES.MODE_ECB)
            except Exception as e:
                raise Exception(f"an error accured, make shure, to use the right key\nerror:{e}")
        else:
            raise Exception("other than ECB not done yet...")
        
        try:
            decrypted_password = cipher.decrypt(encrypted_bytes)
            bytetext = unpad(decrypted_password, AES.block_size)
            return bytetext.decode(self.encoding)
        except:
            raise Exception(f"error decrypting {byte_key}")

    def compare_encrypted(self, password_guess: str, key_guess: str, encrypted_password: bytes) -> bool:
        """
        Vor.: Die validen Argumente -password_guess- -key_guess- als String & das Verschlüsselte Passwort -encrypted_password- im Byteformat
        Eff.: --
        Erg.: Gibt einen Wahrheitswert darüber wieder, ob das versuchte Passwort mit entsprechendem Schlüssel dem Verschlüsselten entspricht
        """
        try:
            encrypted_passwordguess = self.encrypting(password_guess, key_guess)
            if encrypted_passwordguess == encrypted_password:
                return True
            else:
                return False    
        except:
            return "couldn't encrypt password"
