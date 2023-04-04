import molecule # importing my shared C library
from io import BytesIO # this import is essential in the parse method later on

molObj = molecule.molecule() # creating an instance of the molecule class/struct from my C library

# These are constants for use later
radius = {'H': 25, 'C': 40, 'O': 40, 'N': 40}
element_name = {'H': 'grey', 'C': 'black', 'O': 'red', 'N': 'blue'}
header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""
footer = """</svg>"""
offsetx = 500
offsety = 500

# The Atom class is responsible for everything related to the atoms in this program
class Atom:
	
	# This is a constructor that initializes a c_atom member variable every-time it's called
	def __init__(self, c_atom):
		self.c_atom = c_atom
		self.z = c_atom.z

	# This is a toString method
	def __str__(self):
		return '''%s'%lf'%lf'%lf"''' % (self.c_atom.element, self.c_atom.x, self.c_atom.y, self.c_atom.z)

	# This is the svg method for the atoms in the Atom class
	def svg(self):
		circleX = (self.c_atom.x * 100) + offsetx
		circleY = (self.c_atom.y * 100) + offsety
		circleR = radius[self.c_atom.element]
		circleColour = element_name[self.c_atom.element]
		return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="%s"/>\n' % (circleX, circleY, circleR, circleColour)

# The Bond class is responsible for everything related to the bonds in a molecule
class Bond:

	# Same idea with the Bond() constructor here as we had for the Atom() constructor
	def __init__(self, c_bond):
		self.c_bond = c_bond
		self.z = c_bond.z

	# Same idea with the Atom toString method
	def __str__(self):
		return '''%d'%d'%d'%lf'%lf'%lf'%lf'%lf'%lf'%lf'%lf"''' % (self.c_bond.a1, self.c_bond.a2, self.c_bond.epairs, self.c_bond.x1, self.c_bond.x2, self.c_bond.y1, self.c_bond.y2, self.c_bond.z, self.c_bond.len, self.c_bond.dx, self.c_bond.dy)

	# TA from the Thursday lab helped me fix this method. All credit goes to them for helping me fix it!
	def svg(self):
		recX1 = self.c_bond.x1 * 100 - self.c_bond.dy * 10 + offsetx
		recY1 = self.c_bond.y1 * 100 + self.c_bond.dx * 10 + offsety
		recX2 = self.c_bond.x2 * 100 + self.c_bond.dy * 10 + offsetx
		recY2 = self.c_bond.y2 * 100 - self.c_bond.dx * 10 + offsety
		recX3 = self.c_bond.x1 * 100 + self.c_bond.dy * 10 + offsetx		
		recY3 = self.c_bond.y1 * 100 - self.c_bond.dx * 10 + offsety
		recX4 = self.c_bond.x2 * 100 - self.c_bond.dy * 10 + offsetx
		recY4 = self.c_bond.y2 * 100 + self.c_bond.dx * 10 + offsety
		return ' <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (recX1, recY1, recX3, recY3, recX2, recY2, recX4, recY4)

# Molecule inherits from the molecule struct/class in our C library
class Molecule(molecule.molecule):

	# ToString method for printing the contents of the molecule class
	def __str__(self):
		return '''%d'%d'%d'%d"''' % (molObj.atom_max, molObj.atom_no, molObj.bond_max, molObj.bond_no)

	# I decided to encapsulate the mergesort computations into one method for enchanced readability
	def mergeAtomBonds(self):
		atomList = []
		bondList = []
		finalString = ""

		for i in range(self.atom_no):
			atomList.append(self.get_atom(i))

		for i in range(self.bond_no):
			bondList.append(self.get_bond(i))

		while len(atomList) and len(bondList) != 0:
			currAtom = Atom(atomList[0])
			currBond = Bond(bondList[0])
			if currAtom.z < currBond.z:
				finalString += currAtom.svg()
				atomList.pop(0)
			else:
				finalString += currBond.svg()
				bondList.pop(0)

		if len(atomList) != 0:
			for atom in atomList:
				finalString += Atom(atom).svg()
		if len(bondList) != 0:
			for bond in bondList:
				finalString += Bond(bond).svg()
		
		return finalString

	# My svg method calls the mergeAtomBonds() method in the same class for creating the molecule svg file
	def svg(self):
		cpyMergArr = self.mergeAtomBonds()
		return header + cpyMergArr + footer

	# My parse method is divided into two different implementations since the server sends different things and the normal MolDisplay sends different objects
	def parse(self, inputFileObject):
		fileLines = inputFileObject.readlines()
		if isinstance(inputFileObject, BytesIO) == False:
			line = fileLines[3].split()
			num_atoms = int(line[0])
			num_bonds = int(line[1])
			atomLines = fileLines[4:4 + num_atoms]
			bondLines = fileLines[4 + num_atoms:4 + num_atoms + num_bonds]
			numAtBoStr = str(num_atoms) + str(num_bonds)
			for aLine in atomLines:
				aValues = aLine.split()
				atomX, atomY, atomZ, atomEle = aValues[:4]
				self.append_atom(str(atomEle), float(atomX), float(atomY), float(atomZ))
			for bLine in bondLines:
				bValues = bLine.split()
				bondA1, bondA2, bondType = bValues[:3]
				self.append_bond(int(bondA1), int(bondA2), int(bondType))
		else:
			line = fileLines[7].split()
			num_atoms = int(line[0])
			num_bonds = int(line[1])
			atomLines = fileLines[8:8 + num_atoms]
			bondLines = fileLines[8 + num_atoms:8 + num_atoms + num_bonds]
			numAtBoStr = str(num_atoms) + str(num_bonds)
			for aLine in atomLines:
				aValues = aLine.split()
				atomX, atomY, atomZ, atomEle = aValues[:4]
				self.append_atom(atomEle.decode('utf-8'), float(atomX), float(atomY), float(atomZ))
			for bLine in bondLines:
				bValues = bLine.split()
				bondA1, bondA2, bondType = bValues[:3]
				self.append_bond(int(bondA1), int(bondA2), int(bondType))
			return numAtBoStr

# My driver code for testing and running the MolDisplay.py
if __name__=="__main__":
	mol = Molecule()

	inputFile = open('testFiles/CID_31260.sdf', 'r')
	mol.parse(inputFile)
	mol.sort()

	for i in range(mol.atom_no):
		atom = mol.get_atom(i)
		newAtom = Atom(atom)
		print(newAtom)

	for i in range(mol.bond_no):
		bond = mol.get_bond(i)
		newBond = Bond(bond)
		print(newBond)

	newSVG_File = open('testFiles/Isopentanol.svg', 'w')
	newSVG_File.write(mol.svg())
	newSVG_File.close()
	inputFile.close()
