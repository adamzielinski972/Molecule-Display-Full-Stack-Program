from http.server import HTTPServer, BaseHTTPRequestHandler;
import socketserver
import sys
import MolDisplay
import urllib.parse
import molsql
import json
import sqlite3
import os

db = molsql.Database(reset=False)
db.create_tables()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/page1.html" #opens page1 as default
        try:
            file_path = self.path.strip("/") #opens the file
            with open(file_path, "rb") as file:
                # Send the response header
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                self.wfile.write(file.read()) #writes the page to the server
        except FileNotFoundError:
            self.send_error(404)# Send a 404 error if the requested file doesn't exist

    def do_POST(self):
        if self.path == "/molecule": #when the user is submitting a molecule

            #grabs and parses passed in data
            contentLen = int(self.headers['Content-Length']) 
            data = self.rfile.read(contentLen).decode('utf-8')
            data = urllib.parse.parse_qs(data)

            #grabs file and molecule name
            fileName = data["sdf_file"][0]
            moleculeName = data["moleculeName"][0]

            fp = open(fileName)
            db.add_molecule(moleculeName, fp, fileName) #creates the molecule in the database

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.end_headers();
        
        elif self.path == "/submitElement": #when the user is submitting an element
            contentLen = int(self.headers['Content-Length'])
            data = self.rfile.read(contentLen).decode('utf-8')
            data = urllib.parse.parse_qs(data)

            #grabs passed in data
            elementNumber = data["elementNumber"][0]
            elementCode = data["elementCode"][0]
            elementName = data["elementName"][0]
            colour1 = data["colour1"][0]
            colour2 = data["colour2"][0]
            colour3 = data["colour3"][0]
            radius = data["radius"][0]

            db['Elements'] = (elementNumber, elementCode, elementName, colour1, colour2, colour3, radius) #adds element information to database

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

        elif self.path == "/deleteElement": #when user wants to delete an element

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = urllib.parse.parse_qs(post_data)
            selected_value = data['value'][0]
            
            conn = sqlite3.connect('molecules.db') #open database
            cursor = conn.cursor()
            
           
            cursor.execute("DELETE FROM Elements WHERE ELEMENT_NAME = ?", (selected_value,)) # Delete the item from the database
            conn.commit()
            
            conn.close()
            
            # Send a response back to the client
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')

        elif self.path == "/getElements": #grabs the elements
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()

            
            cursor.execute('SELECT ELEMENT_NAME FROM Elements') #gets the elements name
            results = cursor.fetchall()

            element_names = [] #creates list for element names
            for result in results:
                element_names.append(result[0]) #grabs all element names

            response = {'element_names': element_names} #creates json object to send back
            json_response = json.dumps(response)

            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_response.encode()) #send the JSON object as a response

        elif self.path == "/getMoleculeNames": #if the user wants to get the molecule names
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()

            cursor.execute('SELECT NAME FROM Molecules')
            results = cursor.fetchall()

            moleculeNames = []
            for result in results:
                moleculeNames.append(result[0]) #gets all the molecules names from database

            response = {'moleculeNames': moleculeNames}
            json_response = json.dumps(response)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_response.encode())
        
        elif self.path == "/getMolNumbers": #grabs the atom and bond numbers from the molecules
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = urllib.parse.parse_qs(post_data)
            name = data['name'][0]

            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute('SELECT NUM_ATOMS, NUM_BONDS FROM Molecules WHERE NAME = ?', (name,))
            row = cursor.fetchone()

            numAtoms, numBonds = row #grabs the number of atoms and number 
            response = {'num_atoms': numAtoms,'num_bonds': numBonds}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))


        elif self.path == "/displayMolecule": #displays molecule
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = urllib.parse.parse_qs(body)
            name = data['name'][0]

            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute('SELECT FILE_NAME FROM Molecules WHERE NAME = ?', (name,)) #grabs file name
            row = cursor.fetchone()
            
            mol = MolDisplay.Molecule()
            fp = open(row[0])
            mol.parseNormal(fp)

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "image/svg+xml" );
            self.send_header( "Content-length", len(mol.svg()) );
            self.end_headers();

            self.wfile.write( bytes(mol.svg(),"utf-8")) #displays the content of the svg string

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

# Start the server
httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), Handler );
httpd.serve_forever();
