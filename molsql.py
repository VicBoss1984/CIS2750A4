# We will need these 3 modules for what we are about to do in this class.
import os
import glob
import sqlite3
import MolDisplay

# The Database class is responsible for everything that pertains to the database operations and the database itself in this assignment
class Database:

	# My intention here was to override the default constructor of this class to always initialize a reset boolean value.
	# This constructor helps us avoid SQL getting angry at us everytime we try to create new tables that already exist in our database.
	def __init__(self, reset = False):
		if reset == True:
			os.remove('molecules.db')
		self.conn = sqlite3.connect('molecules.db')

	# My intention for this method is to create a bunch of tables with unique constraints applied to each one of them.
	# I am doing this through embedded SQL commands.
	# My tables should then be used to store the molecular data that my sequential functions will generate.
	# Note that the constraints may seem unusual at first, but they are essential to creating the correct tables for the program.
	def create_tables(self):
		
		self.conn.execute("""CREATE TABLE if not exists Elements (
						ELEMENT_NO 		INTEGER NOT NULL,
						ELEMENT_CODE 	VARCHAR(3) NOT NULL,
						ELEMENT_NAME 	VARCHAR(32) NOT NULL,
						COLOUR1 		CHAR(6) NOT NULL,
						COLOUR2 		CHAR(6) NOT NULL,
						COLOUR3 		CHAR(6) NOT NULL,
						RADIUS 			DECIMAL(3) NOT NULL,
						PRIMARY KEY(ELEMENT_CODE));""")

		self.conn.execute("""CREATE TABLE if not exists Atoms (
						ATOM_ID 		INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
						ELEMENT_CODE 	VARCHAR(3) NOT NULL,
						X 				DECIMAL(7, 4) NOT NULL,
						Y 				DECIMAL(7, 4) NOT NULL,
						Z 				DECIMAL(7, 4) NOT NULL,
						FOREIGN KEY(ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE));""")

		self.conn.execute("""CREATE TABLE if not exists Bonds (
						BOND_ID 		INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
						A1 				INTEGER NOT NULL,
						A2 				INTEGER NOT NULL,
						EPAIRS 			INTEGER NOT NULL);""")

		self.conn.execute("""CREATE TABLE if not exists Molecules (
						MOLECULE_ID 	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
						NAME 			TEXT NOT NULL UNIQUE);""")

		self.conn.execute("""CREATE TABLE if not exists MoleculeAtom (
						MOLECULE_ID 	INTEGER NOT NULL,
						ATOM_ID 		INTEGER NOT NULL,
						PRIMARY KEY(MOLECULE_ID, ATOM_ID),
						FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules,
						FOREIGN KEY(ATOM_ID) REFERENCES Atoms);""")

		self.conn.execute("""CREATE TABLE if not exists MoleculeBond (
						MOLECULE_ID 	INTEGER NOT NULL,
						BOND_ID 		INTEGER NOT NULL,
						PRIMARY KEY(MOLECULE_ID, BOND_ID),
						FOREIGN KEY(MOLECULE_ID) REFERENCES Molecules,
						FOREIGN KEY(BOND_ID) REFERENCES Bonds);""")


	# We are overriding the setitem() default method because we want to perform operator overloading on the '[]' operators later.
	# My intention with this method is to create a query string that can accept any given table as an argument.
	def __setitem__(self, table, values):
		query = f"INSERT INTO {table} VALUES ({', '.join('?' * len(values))})"
		self.conn.execute(query, values)
		self.conn.commit()

	# My intention with add_atom is to provide a method in the Database class that takes in the information of the atoms.
	# add_atom() should employ operator overloading for the '[]' to create a tuple that contains the atom's information.
	# We are not supposed to be inserting anything into the SQL tables here; we just need to retrieve atomID and molID of the atom and molecule in-question.
	def add_atom(self, molName, atom):
		self["Atoms"] = (atom.elementCode, atom.x, atom.y, atom.z)
		atomID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
		molID = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molName,)).fetchone()[0]
		self["MoleculeAtom"] = (molID, atomID)

	# Same as add_atom, but for bonds.
	def add_bond(self, molName, bond):
		self["Bonds"] = (bond.a1, bond.a2, bond.epairs)
		bondID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
		molID = self.conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molName,)).fetchone()[0]
		self["MoleculeBond"] = (molID, bondID)

	# My plan with the add_molecule() method was to perform the SQL INSERT commands in the correct tables and columns using add_atom and add_bond.
	# The parser from MolDisplay.py is coming in handy here as it's how we're getting our input from the .sdf files processed into readable chunks.
	# Since we can't hardcode the individual atoms and bonds, we need to tell the SQL engine that we don't know exactly what we are expecting but that we still know which variable will hold the value we need.
	def add_molecule(self, molName, fp):
		molecule = MolDisplay.Molecule()
		molecule.parse(fp)

		totalAtoms = molecule.atom_no
		totalBonds = molecule.bond_no

		self.conn.execute("INSERT INTO Molecules (name) VALUES (?)", (molName,))
		moleculeID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

		for i in range(totalAtoms):
			atom = molecule.get_atom(i)
			self.conn.execute("INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)", (atom.element, atom.x, atom.y, atom.z))
			atomID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
			self.conn.execute("INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)", (moleculeID, atomID))

		for i in range(totalBonds):
			bond = molecule.get_bond(i)
			self.conn.execute("INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)", (bond.a1, bond.a2, bond.epairs))
			bondID = self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
			self.conn.execute("INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)", (moleculeID, bondID))

		self.conn.commit()

	def load_mol(self, name):
		molecule = MolDisplay.Molecule()

		queryAtoms = """SELECT Atoms.ATOM_ID, Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z
							 FROM Atoms
							 JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
							 JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
							 WHERE Molecules.NAME = ?
							 ORDER BY Atoms.ATOM_ID"""
		atoms = self.conn.execute(queryAtoms, (name,)).fetchall()

		for atom in atoms:
			molecule.append_atom(atom[1], atom[2], atom[3], atom[4])

		queryBonds = """SELECT Bonds.BOND_ID, Bonds.A1, Bonds.A2, Bonds.EPAIRS
							 FROM Bonds
							 JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
							 JOIN Molecules ON MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
							 WHERE Molecules.NAME = ?
							 ORDER BY Bonds.BOND_ID"""
		bonds = self.conn.execute(queryBonds, (name,)).fetchall()

		for bondID, a1, a2, epairs in bonds:
			molecule.append_bond(a1, a2, epairs)

		return molecule

	def radius(self):
		result = self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements").fetchall()
		myResDic = dict(result)
		return myResDic

	def element_name(self):
		result = self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements").fetchall()
		myResDic = dict(result)
		return myResDic

	def radial_gradients(self):
		elements = self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements").fetchall()
		radialGradientSVG = """
			<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
				<stop offset="0%%" stop-color="#%s"/>
				<stop offset="50%%" stop-color="#%s"/>
				<stop offset="100%%" stop-color="#%s"/>
			</radialGradient>"""

		return ''.join([radialGradientSVG % (element_name, color1, color2, color3) for element_name, color1, color2, color3 in elements])

	def createDatabase(self):
		db = Database(reset = True)
		db.create_tables()

		db['Elements'] = (1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25)
		db['Elements'] = (6, 'C', 'Carbon', '808080', '010101', '000000', 40)
		db['Elements'] = (7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40)
		db['Elements'] = (8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40)
		sdf_dir = 'testFiles/'
		db.read_files(sdf_dir)

	def get_list_mol(self):
		listMol = self.conn.execute("SELECT NAME FROM Molecules").fetchall()
		return listMol

	def read_files(self, sdf_dir):
		sdf_files = glob.glob(os.path.join(sdf_dir, '*.sdf'))
		for sdf_file in sdf_files:
			mol = os.path.splitext(os.path.basename(sdf_file))[0]
			with open(sdf_file) as fp:
				self.add_molecule(mol, fp)

	def write_svg_files(self):
		db = Database(reset = False)
		listMol = db.get_list_mol()
		svgDir = "svgFiles"

		if not os.path.exists(svgDir):
			os.makedirs(svgDir)

		for tupleMol in range(len(listMol)):
			tupleMol = listMol[tupleMol]
			for molStr in range(len(tupleMol)):
				molStr = tupleMol[molStr]
				molecule = db.load_mol(molStr)
				molecule.sort()
				svgFilePath = os.path.join(svgDir, f"{molStr}.svg")
				with open(svgFilePath, "w") as fp:
					fp.write(molecule.svg())

	def add_element(self, element_name, element_code, element_num, element_radius, element_col1, element_col2, element_col3):
		query = """INSERT INTO Elements (ELEMENT_NAME, ELEMENT_NO, ELEMENT_CODE, COLOUR1, COLOUR2, COLOUR3, RADIUS) 
    	VALUES (?, ?, ?, ?, ?, ?, ?)"""
		self.conn.execute(query, (element_name, element_num, element_code, element_col1, element_col2, element_col3, element_radius))
		self.conn.commit()

	def remove_element(self, element_name, element_code, element_num, element_radius, element_col1, element_col2, element_col3):
		query = """DELETE FROM Elements 
		WHERE ELEMENT_NAME = ? AND ELEMENT_NO = ? AND ELEMENT_CODE = ? AND RADIUS = ? AND 
		COLOUR1 = ? AND COLOUR2 = ? AND COLOUR3 = ?"""
		cursor = self.conn.execute(query, (element_name, element_code, element_num, element_radius, element_col1, element_col2, element_col3))
		self.conn.commit()
		return cursor.rowcount

if __name__ == "__main__":
	db = Database(reset = False)
	db.createDatabase()
	MolDisplay.radius = db.radius()
	MolDisplay.elementName = db.element_name()
	MolDisplay.header += db.radial_gradients()
	db.write_svg_files()