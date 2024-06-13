import os;
import sqlite3;
from MolDisplay import Molecule
import MolDisplay


class Database:
    def __init__(self, reset=False):
        if reset: #checks if the reset value is true
            if os.path.exists("molecules.db"):
                os.remove("molecules.db") #removes the old database

        self.conn = sqlite3.connect("molecules.db") #creates the database
        self.cursor = self.conn.cursor() #creates a cursor 
        self.conn.commit() #commits changes
    
    def create_tables(self): #creates tables
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Elements(
                        ELEMENT_NO INTEGER NOT NULL,
                        ELEMENT_CODE VARCHAR(3) PRIMARY KEY NOT NULL,
                        ELEMENT_NAME VARCHAR(32) NOT NULL,
                        COLOUR1 CHAR(6) NOT NULL,
                        COLOUR2 CHAR(6) NOT NULL,
                        COLOUR3 CHAR(6) NOT NULL,
                        RADIUS DECIMAL(3) NOT NULL
                        )
            """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Atoms (ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        ELEMENT_CODE VARCHAR(3) NOT NULL,
                        X DECIMAL(7,4) NOT NULL,
                        Y DECIMAL(7,4) NOT NULL,
                        Z DECIMAL(7,4) NOT NULL,
                        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements (ELEMENT_CODE) 
                        )
            """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bonds (
                        BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        A1 INTEGER NOT NULL,
                        A2 INTEGER NOT NULL,
                        EPAIRS INTEGER NOT NULL
                        )
            """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Molecules (
                        MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        NAME TEXT UNIQUE NOT NULL,
                        NUM_ATOMS INTEGER,
                        NUM_BONDS INTEGER,
                        FILE_NAME VARCHAR(32) NOT NULL
                        )
            """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MoleculeAtom (
                        MOLECULE_ID INTEGER NOT NULL,
                        ATOM_ID INTEGER NOT NULL,
                        PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                        FOREIGN KEY (ATOM_ID) REFERENCES Atoms (ATOM_ID)
                        )
            """)
                                
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MoleculeBond (
                        MOLECULE_ID INTEGER NOT NULL,
                        BOND_ID INTEGER NOT NULL,
                        PRIMARY KEY (MOLECULE_ID, BOND_ID),
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                        FOREIGN KEY (BOND_ID) REFERENCES Bonds (ATOM_ID)
                        )
            """)

        self.conn.commit()

    def __setitem__ (self, table, values):

        #combines table and values to use key indexing to set values
        first = "(" + ",".join(["?"] * len(values)) + ")" 
        newVals = f"INSERT INTO {table} VALUES {first}"

        self.cursor.execute(newVals, values) #inserts info
        
        self.conn.commit()

    def add_atom(self, molname, atom):

        self.cursor.execute("""
            INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z)
            VALUES (?, ?, ?, ?)
        """, (atom.element, atom.x, atom.y, atom.z)) #inserts info into table using passed in atom

        atomID = self.cursor.lastrowid #grabs the id from the table

        self.cursor.execute("""
            SELECT MOLECULE_ID
            FROM Molecules
            WHERE NAME = ?
        """, (molname,)) #selects the molecules id that corresponds with the passed in name

        moleculeID = self.cursor.fetchone()[0] #grabs id
        
        self.cursor.execute("""
            INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID)
            VALUES (?, ?)
        """, (moleculeID, atomID)) #adds values to table

        self.conn.commit() 

    def add_bond(self, molname, bond):

        self.cursor.execute("""
            INSERT INTO Bonds (A1, A2, EPAIRS)
            VALUES (?, ?, ?)
        """, (bond.a1, bond.a2, bond.epairs)) #inserts values into table using passed in bond

        bondID = self.cursor.lastrowid #grabs id of the bond

        self.cursor.execute("""
            SELECT MOLECULE_ID
            FROM Molecules
            WHERE NAME = ?
        """, (molname,)) 

        moleculeID = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID)
            VALUES (?, ?)
        """, (moleculeID, bondID)) #adds info from molecule and bond to the corresponding table

        self.conn.commit()

    def add_molecule(self, name, fp, fileName):

        molecule = Molecule() #creates object
        nums = molecule.parseNormal(fp) #gets atom and bond numbers from list

        self["Molecules"] = (None,name,nums[0],nums[1],fileName) #creates blank table
        
        for i in range(nums[0]): #calls function for number of atoms
            atom = molecule.get_atom(i)
            self.add_atom(name, atom)

        for i in range(nums[1]): #calls function for number of bonds
            bond = molecule.get_bond(i)
            self.add_bond(name, bond)

        self.conn.commit()

    def load_mol(self, name):
        
        molecule = MolDisplay.Molecule()
        
        atomsList = self.conn.execute( ("""SELECT *
                        FROM Atoms, MoleculeAtom, Molecules
                        WHERE Atoms.ATOM_ID = MoleculeAtom.ATOM_ID AND Molecules.NAME = ? AND Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                        ORDER BY ATOM_ID ASC
                    """), (name,)).fetchall() #uses the name of the molecule to get its atoms from the table

        bondsList = self.conn.execute( ("""SELECT *
                        FROM Bonds, MoleculeBond, Molecules
                        WHERE Bonds.BOND_ID = MoleculeBond.BOND_ID AND Molecules.NAME = ? AND Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                        ORDER BY BOND_ID ASC
                    """), (name,)).fetchall() #uses the name of the molecule to get its bonds from the table

        for atom in atomsList: #runs through atoms
            molecule.append_atom(atom[1], atom[2], atom[3], atom[4]) #creates atom using the info from the table

        #for bond in bondsArr:
            #mol.append_bond(bond[1],bond[2],bond[3])

        #I HAVE NO CLUE WHY THIS DOESN'T WORK^
            
        return molecule #returns the object
    
    def radius(self):
        
        radiusDicionary = {}

        arr = self.cursor.execute("""
            SELECT ELEMENT_CODE, RADIUS
            FROM Elements
        """) #gets the element code and radius

        rowList = self.cursor.fetchall() #grabs the info from all the rows

        for row in rowList: #runs through rows of tables
            element = row[0] #gets element
            radius = row[1] #gets radius
            radiusDicionary[element] = radius #adds to dicionary

        
        return radiusDicionary #return the dictionary

    def element_name(self): #works the same as above but for the code and name
        
        elementDictionary = {}

        self.cursor.execute("""
            SELECT ELEMENT_CODE, ELEMENT_NAME
            FROM Elements
        """)

        rowList = self.cursor.fetchall()
   
        for row in rowList:
            element = row[0]
            elementName = row[1]
            elementDictionary[element] = elementName

        return elementDictionary

    def radial_gradients(self):

        svgString = ""
        
        self.cursor.execute("""
            SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3
            FROM Elements
        """) #find info from table

        rowList = self.cursor.fetchall() #puts all the rows in alsit

        for row in rowList:
            
            #assings info from row
            elementName = row[0]
            colour1 = row[1]
            colour2 = row[2]
            colour3 = row[3]

            #fills string with info
            radialGradient = f"""
            <radialGradient id="{elementName}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
                <stop offset="0%" stop-color="#{colour1}"/>
                <stop offset="50%" stop-color="#{colour2}"/>
                <stop offset="100%" stop-color="#{colour3}"/>
            </radialGradient>
            """
            svgString += radialGradient #adds radius info to the svg string

        return svgString #returns the string
