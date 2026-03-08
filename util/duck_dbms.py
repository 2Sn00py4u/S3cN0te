import duckdb as duck
import pandas as pd
import os

class DBMS:
    def __init__(self, DBfilePath:str) -> duck.DuckDBPyConnection:
        """
        Vor.: Valider DB-Pfad
        Eff.: Verbindung zu Datenbank wird hergestellt
        Erg.: Interaktion mit Datenbank via Verbindung
        """
        self.DBpath = DBfilePath
        self.__dbConnection = duck.connect(self.DBpath)
        self.__Tables = self.getTables()
        
    def importCSV(self, csvPath: str, tableName: str) -> None:
        """
        Vor.: Valider csv-Pfad und Tabellenname
        Eff.: csv-Datei wird geöffnet und gelesen; Daten werden in die Datenbank importiert
        Erg.: Datenbanktabelle mit gelesenen Daten
        """
        with open(csvPath, "r") as csvFile:
            attributes = []
            values = []
            for i, line in enumerate(csvFile):
                if i == 0:
                    line = line.split(";")
                    line.pop(len(line)-1)
                    attributes = line
                else:
                    line = line.split(";")
                    line.pop(len(line)-1)
                    values.append(tuple(line))
            csvFile.close()
        if tableName in self.getTables():
            self.deleteTable(tableName)
        self.createTable(tableName, attributes)
        self.insertValues(tableName, values)
        
    """  get-functions  """
    def getConnection(self) -> duck.DuckDBPyConnection:
        """
        Vor.: --
        Eff.: --
        Erg.: Verbindung wird zurückgegeben
        """
        return self.__dbConnection
    
    def getTables(self, pdOutput: bool = False) -> list|pd.DataFrame:
        """
        Vor.: --
        Eff.: --
        Erg.: Tabelle(n) der Datenbank werden zurückgegeben
        pdOutput: Gibt an, ob die Ausgabe als Pandas DataFrame oder als Liste von
        """
        if pdOutput == True:
            return self.execute("""SHOW TABLES""", pdOutput)
        else:
            tables = []
            tableTuples = self.execute("""SHOW TABLES""", pdOutput)
            for i in range(len(tableTuples)):
                tables.append(tableTuples[i][0])
            return tables

    def getAttributes(self, table: str,pdOutput: bool = False) -> list|pd.DataFrame:
        """
        Vor.: Tabelle existiert
        Eff.: --
        Erg.: Attribute der Tabelle werden zurückgegeben
        pdOutput: Gibt an, ob die Ausgabe als Pandas DataFrame oder als Liste von Tupeln erfolgen soll
        """
        return self.execute(f"""PRAGMA table_info({table})""", pdOutput)
    
    """  key-functions  """
    def connectDB(self, dbPath: str) -> None:
        """
        Vor.: --
        Eff.: --
        Erg.: Verbindung zur Datenbank wird hergestellt
        """
        try:
            self.disconnectDB()
        except:
            pass
        self.__dbConnection = duck.connect(dbPath)
    
    def createTable(self, tableName: str, tableAttributes: list[str]) -> None:
        """
        Vor.: Name der Tabelle und Attribute sind bekannt
        Eff.: Eintrag in die Datenbank
        Erg.: Eine neue Tabelle wird erstellt, falls sie nicht existiert
        """
        try:
            command = f"""CREATE TABLE IF NOT EXISTS {tableName}("""
            for i in range(len(tableAttributes)-1):
                command += f"{tableAttributes[i]},"
            command+= f"{tableAttributes[len(tableAttributes)-1]})"
            self.execute(command)
        except:
            raise Exception(f"error creating table {tableName}")

    def insertValues(self, table: str, rows: list[tuple,tuple]) -> None:
        """
        Vor.: Tabelle existiert und Attribute sind bekannt
        Eff.: Ein neues Tuple wird in die Tabelle eingefügt
        Erg.: Ein neues Tuple in der Tabelle
        """
        insertCommand = f"""INSERT INTO {table} ("""
        attributes = []
        for attributeInfo in self.getAttributes(table):
            attributes.append(attributeInfo[1])
        for i, attribute in enumerate(attributes):
            if i == len(attributes)-1:
                insertCommand += f"{attribute}) "
            else:
                insertCommand += f"{attribute},"
        insertCommand += "VALUES ("
        for i, attribute in enumerate(attributes):
            if i == len(attributes)-1:
                insertCommand += "?) "
            else:
                insertCommand += "?,"
                
        for row in rows:
            self.__dbConnection.execute(insertCommand, row)
        self.__dbConnection.commit()
    
    def deleteValues(self, table: str, condition: str, *args) -> bool:
        """
        Vor.: Tabelle existiert und Bedingung ist bekannt
        Eff.: In der Datenbank gespeicherte Werte werden gelöscht
        Erg.: Datentuple gelöscht, falls Bedingung erfüllt ist
        """
        deleted = False
        try:
            self.execute(f"""DELETE FROM {table} WHERE {condition}""", False, args)
            deleted = True
        except Exception as e:
            print(e)
        return deleted
    
    def addCollumn(self, table: str, collumnName: str, collumnType: str) -> None:
        """
        Vor.: Tabelle existiert und Name sowie Typ der neuen Spalte sind bekannt
        Eff.: Neue Spalte wird in der Tabelle hinzugefügt
        Erg.: Neue Spalte in der Tabelle
        """
        self.execute(f"""ALTER TABLE {table} ADD COLUMN {collumnName} {collumnType}""")
    
    def renameTable(self, table: str, newTablename: str) -> None:
        """
        Vor.: Tabelle existiert und neuer Name ist bekannt
        Eff.: In der DB gespeicherte Tabelle wird überschrieben
        Erg.: Neuer Tabellenname in der Datenbank
        """
        self.execute(f"""ALTER TABLE {table} RENAME TO {newTablename}""")
    
    def deleteTable(self, table: str) -> None:
        """
        Vor.: --
        Eff.: In der Datenbank gespeicherte Tabelle wird überschrieben
        Erg.: Tabelle wurde gelöscht
        """
        self.execute(f"""DROP TABLE IF EXISTS {table}""")
    
    def disconnectDB(self) -> None:
        """
        Vor.: --
        Eff.: --
        Erg.: Verbindung wird geschlossen
        """
        self.__dbConnection.close()
    
    def deleteDB(self)-> None:
        """
        Vor.: --
        Eff.: Die assoziierte Datenbankdatei wird gelöscht
        Erg.: DB-datei gelöscht
        """
        try:
            os.remove(self.DBpath)
        except Exception as e:
            raise Exception(f"error deleting self:\n{e}")
    
    def execute(self, command:str, pdOutput: bool= False, *args) -> list[tuple]|pd.DataFrame:
        """
        Vor.: Befehl ist bekannt + zusätzliche Argumente
        Eff.: SQL-Befehl wird in der Datenbank ausgeführt
        Erg.: Output des Befehls wird zurückgegeben
        pdOutput: Gibt an, ob die Ausgabe als Pandas DataFrame oder als Liste von
        """
        if not args:
            result = self.__dbConnection.execute(command).fetchall()
        else:
            result = self.__dbConnection.execute(command, args).fetchall()
        
        if not pdOutput:
            return result
        else:
            try:
                pandasOutput = pd.DataFrame(result)
                return duck.sql("""SELECT * FROM pandasOutput""")
            except:
                return "min 1 value"
            
    
    """  Magische Methoden  """
    def __str__(self) -> str:
        return "class for interacting with a DB via duckdb"
