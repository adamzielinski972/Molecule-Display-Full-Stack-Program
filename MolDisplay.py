import molecule
import io

radius = {  'H': 25,
            'C': 40,
            'O': 40,
            'N': 40,
        };

element_name = {'H': 'grey',
                'C': 'black',
                'O': 'red',
                'N': 'blue',
            };

epairs =    {'1' : 1,
             '01': 1,
             '2' : 2,
             '02': 2,
             '3' : 3,
             '03': 3,
             '4' : 4,
             '04': 4.
        }       


header = """<svg version="1.1" width="1000" height="1000"
                xmlns="http://www.w3.org/2000/svg">""";

footer = """</svg>""";

offsetx = 500;
offsety = 500;

def Atom (c_atom): #atom wrapper class

    class Wrapper:

        def __init__ (self, c_atom): #sets the atom to be the passed in atom structure
            self.wrap = c_atom
            self.z = c_atom.z
        
        def __str__  (self):
            return f'{self.wrap.element} {self.wrap.x} {self.wrap.y} {self.wrap.z}'#returns atom members
        
        def svg(self): #returns svg formatted string using the atom information
            return ('  <circle cx="%.2f" cy="%.2f" r="%d" fill="%s"/>\n' % (self.wrap.x * 100 + offsetx, self.wrap.y * 100 + offsety, radius[self.wrap.element],element_name[self.wrap.element]))

    return Wrapper#retunrs the wrapped class

@Atom
class Atom: #base class which takes in the c structure and turns it into a python class
    def __init__(self, c_atom):
        self.x = c_atom.x
        self.y = c_atom.y
        self.z = c_atom.z
        self.element = c_atom.element

def Bond(c_bond):
    
    class Wrapper:
        
        def __init__(self, c_bond):
            self.wrap = c_bond
            self.z = c_bond.z
            
        def __str__(self):
            return f'{self.wrap.a1} {self.wrap.a2} {self.wrap.epairs} {self.wrap.x1} {self.wrap.x2} {self.wrap.y1} {self.wrap.y2} {self.wrap.z} {self.wrap.len} {self.wrap.dx} {self.wrap.dy}'
        
        def svg(self): #uses the atom x and y and the offset and dx and dy to calculate polygon end points
            return ('  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (((self.wrap.x1 * 100 + offsetx)-(self.wrap.dy*10)), ((self.wrap.y1 * 100 + offsety)+(self.wrap.dx*10)), ((self.wrap.x1 * 100 + offsetx)+(self.wrap.dy*10)), ((self.wrap.y1 * 100 + offsety)-(self.wrap.dx*10)), ((self.wrap.x2 * 100 + offsetx)+(self.wrap.dy*10)), ((self.wrap.y2 * 100 + offsety)-(self.wrap.dx*10)), ((self.wrap.x2 * 100 + offsetx)-(self.wrap.dy*10)), ((self.wrap.y2 * 100 + offsety)+(self.wrap.dx*10))))
        
    return Wrapper

@Bond
class Bond: #bond base class for converting the c structure
    def __init__(self, c_bond):
        self.a1 = c_bond.a1
        self.a2 = c_bond.a2
        self.epairs = c_bond.epairs
        self.atoms = c_bond.atoms
        self.x1 = c_bond.x1
        self.x2 = c_bond.x2
        self.y1 = c_bond.y1
        self.y2 = c_bond.y2
        self.z = c_bond.z
        self.len = c_bond.len
        self.dx = c_bond.dx
        self.dy = c_bond.dy

class Molecule (molecule.molecule): #molecule subclass which takes in c molecule

    def __str__(self):
        return f'{self.get_bond(1).a1}'
    
    def sort(self): 
        i = 0
        j = 0
        sortedList = []
        atomList = []
        bondList = []

        while i < self.bond_no: #adds all the bonds to a lst
            bondList.append(self.get_bond(i))
            i += 1

        while j < self.atom_no: #adds all the atoms to a list
            atomList.append(self.get_atom(j))
            j += 1

        i = 0
        j = 0

        while i < self.bond_no and j < self.atom_no: #runs through each list
            if bondList[i].z < atomList[j].z: #checks if the bond has a lesser z value
                sortedList.append(bondList[i]) #adds to sort
                i += 1
            else: #if the atom has a less z value
                sortedList.append(atomList[j])
                j += 1

        sortedList = sortedList + bondList[i:] + atomList[j:] #adds the remainder of the elements from the other list once one list has been exhausted

        return sortedList #returns the lsit

    def svg(self):
        sortedList = self.sort() #calls the sort function to get the sorted list
        atom = type(self.get_atom(0)) #gets atom type  
        bond = type(self.get_bond(0)) #gets bond type

        returnString = "" #intial svg string

        returnString += header #adds header
        
        i = 0
        while i < len(sortedList): #runs through sorted list
            if type(sortedList[i]) == atom: #if it is an atom
                temp = Atom(sortedList[i])#create an atom object
                returnString += temp.svg()#add its svg to the string
            else: #if it is a bond 
                temp2 = Bond(sortedList[i])#create a bond object
                returnString += temp2.svg()#adds its svg to the string
            i += 1

        returnString += footer #adds footer

        return returnString #returns completed svg string
    
    def parseNormal(self,file):
        file.readline()
        file.readline()
        file.readline()

        firstSplit = (file.readline()).split()
        atomNo = int(firstSplit[0]) #gets atom number
        bondNo = int(firstSplit[1]) #gets bond number
        
        nums = []
        nums.append(atomNo)
        nums.append(bondNo)

        lines = [] #creates and empty array for the remainder of the information
        i = 0
        while i < bondNo+atomNo: #runs through atom lines plus bond lines
            lines.append(file.readline())#adds lines to array
            i += 1

        i = 0
        while i < bondNo+atomNo: #runs through atom lines plus bond lines
            temp = lines[i].split() #splits the line up
            if i < atomNo: #if it is an atom
                self.append_atom(temp[3],float(temp[0]),float(temp[1]),float(temp[2])) #append atom using split info
            else: #if it is a bond
                #print(int(temp[0]) - 1,int(temp[1]) - 1,epairs[temp[2]])
                self.append_bond(int(temp[0]),int(temp[1]),epairs[temp[2]]) #append bond using split info
            i += 1

        return nums