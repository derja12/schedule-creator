import json
import sys
from http import cookies
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs
from passlib.hash import bcrypt
import database
from session_store import SessionStore

SESSION_STORE = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    # load cookie data from client via the Cookie header
    def load_cookie(self):
        print("request headers:", self.headers)

        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            self.cookie = cookies.SimpleCookie()

        

    # send cookie data to client via the Set-Cookie header
    def send_cookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie", morsel.OutputString())
        # for morsel in self.cookie:
        #     self.send_header("Set-Cookie", self.cookie[morsel].OutputString())
        
    # load session data info into self.sessionData
    def load_session(self):
        self.load_cookie()
        
        if "sessionID" in self.cookie:
            sessionID = self.cookie["sessionID"].value
            self.sessionData = SESSION_STORE.getSessionData(sessionID)
            if self.sessionData == None:
                sessionID = SESSION_STORE.createSession()
                self.cookie["sessionID"] = sessionID
                self.sessionData = SESSION_STORE.getSessionData(sessionID)
        else:
            sessionID = SESSION_STORE.createSession()
            self.cookie["sessionID"] = sessionID
            self.sessionData = SESSION_STORE.getSessionData(sessionID)
        self.cookie["sessionID"]["samesite"] = "None"
        self.cookie["sessionID"]["secure"] = True

#   END_HEADERS OVERRIDE
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"]) # pseudo-wildcard
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_cookie()
        BaseHTTPRequestHandler.end_headers(self)

#          GET

#   GET(employees)
    def handleGetEmployees(self):
        # EXAMPLE OF NOT LOGGED IN 401
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        db = database.LabbieDB()
        employees = db.getEmployees()
        
        self.wfile.write(bytes(json.dumps(employees), "utf-8"))

#   GET(employee by id)
    def handleGetEmployeeByID(self, member_id):
        # EXAMPLE OF NOT LOGGED IN 401
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
        db = database.LabbieDB()
        employee = db.getEmployeeByID(member_id)
        print("    EMPLOYEE ----------->", employee)

        if employee:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps(employee), "utf-8"))
        else:
            self.handle404()

#   GET(sessions)
    def handleGetSessions(self):
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
        if self.sessionData["userID"] is None:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()

#          POST

#   POST(employees)
    def handlePostEmployee(self):
        # EXAMPLE OF NOT LOGGED IN 401
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
            
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8") # opposite of bytes() function from line 21
        print("    raw body ----------->", request_body)
        
        parsed_body = parse_qs(request_body) # IMPORT
        print("    parsed body -------->", parsed_body)

        if "name" in parsed_body:
            name = parsed_body["name"][0]
        else:
            name = "____"

        if "totalhours" in parsed_body:
            totalhours = parsed_body["totalhours"][0]
        else:
            totalhours = 0

        if "shiftcolor" in parsed_body:
            shiftcolor = parsed_body["shiftcolor"][0]
        else:
            shiftcolor = "#FFFFFF"

        if "monhours" in parsed_body:
            monhours = parsed_body["monhours"][0]
        else:
            monhours = None

        if "tuehours" in parsed_body:
            tuehours = parsed_body["tuehours"][0]
        else:
            tuehours = None

        if "wedhours" in parsed_body:
            wedhours = parsed_body["wedhours"][0]
        else:
            wedhours = None

        if "thurhours" in parsed_body:
            thurhours = parsed_body["thurhours"][0]
        else:
            thurhours = None

        if "frihours" in parsed_body:
            frihours = parsed_body["frihours"][0]
        else:
            frihours = None      

        if "sathours" in parsed_body:
            sathours = parsed_body["sathours"][0]
        else:
            sathours = None        

        db = database.LabbieDB()
        db.createEmployee(name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours)

        self.send_response(201)
        self.end_headers()

#   POST(user)
    def handlePostUser(self):
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8") # opposite of bytes() function from line 21
        print("    raw body ----------->", request_body)
        
        parsed_body = parse_qs(request_body) # IMPORT
        print("    parsed body -------->", parsed_body)

        if "email" in parsed_body:
            email = parsed_body["email"][0]
        else:
            email = ""
            print("EMAIL NOT IN PARSED BODY!!!")

        if "password" in parsed_body:
            password = parsed_body["password"][0]
        else:
            password = ""
            print("PASSWORD NOT IN PARSED BODY!!!")

        if "firstName" in parsed_body:
            fName = parsed_body["firstName"][0]
        else:
            fName = ""
            print("FIRSTNAME NOT IN PARSED BODY!!!")

        if "lastName" in parsed_body:
            lName = parsed_body["lastName"][0]
        else:
            lName = ""
            print("LASTNAME NOT IN PARSED BODY!!!")

        db = database.LabbieDB()
        emailExists = db.getUserByEmail(email)
        if not emailExists:
            encryptedPassword = bcrypt.hash(password)
            db.createUser(email, encryptedPassword, fName, lName)
            self.send_response(201)
            self.end_headers()
        else:
            self.send_response(422)
            self.end_headers()

#   POST(session)
    def handleAuthenticateUser(self):
        length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(length).decode("utf-8") # opposite of bytes() function from line 21
        print("    raw body ----------->", request_body)
        
        parsed_body = parse_qs(request_body) # IMPORT
        print("    parsed body -------->", parsed_body)

        if "email" in parsed_body:
            email = parsed_body["email"][0]
        else:
            email = ""
            print("EMAIL NOT IN PARSED BODY!!!")

        if "password" in parsed_body:
            password = parsed_body["password"][0]
        else:
            password = ""
            print("PASSWORD NOT IN PARSED BODY!!!")

        db = database.LabbieDB()
        user = db.getUserByEmail(email)
        if not user:
            self.send_response(401)
            self.end_headers()
        else:
            loginSuccess = bcrypt.verify(password, user["password"])
            if loginSuccess:
                self.sessionData["userID"] = user["id"]
                self.send_response(201)
                self.end_headers()
            else:
                self.send_response(401)
                self.end_headers()

#          DELETE

#   DELETE(employee by id)
    def handleDeleteEmployeeByID(self,id):
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
        db = database.LabbieDB()
        employee = db.getEmployeeByID(id)
        print("    EMPLOYEE ----------->", employee)

        if employee:
            db.deleteEmployeeByID(id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps(employee), "utf-8"))
        else:
            self.handle404()

#   DELETE(session)
    def handleLogoutUser(self):
        if "userID" in self.sessionData:
            self.sessionData["userID"] = None
        self.send_response(200)
        self.end_headers()


#          PUT

#   PUT(employee by id)
    def handleReplaceEmployeeByID(self, id):
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
        db = database.LabbieDB()
        employee = db.getEmployeeByID(id)
        print("    EMPLOYEE ----------->", employee)

        
        if employee:

            length = int(self.headers["Content-Length"])
            request_body = self.rfile.read(length).decode("utf-8") # opposite of bytes() function from line 21
            print("    raw body ----------->", request_body)
            
            parsed_body = parse_qs(request_body) # IMPORT
            print("    parsed body -------->", parsed_body)

            if "name" in parsed_body:
                name = parsed_body["name"][0]
            else:
                name = "____"

            if "totalhours" in parsed_body:
                totalhours = parsed_body["totalhours"][0]
            else:
                totalhours = 0

            if "shiftcolor" in parsed_body:
                shiftcolor = parsed_body["shiftcolor"][0]
            else:
                shiftcolor = "#FFFFFF"

            if "monhours" in parsed_body:
                monhours = parsed_body["monhours"][0]
            else:
                monhours = None

            if "tuehours" in parsed_body:
                tuehours = parsed_body["tuehours"][0]
            else:
                tuehours = None

            if "wedhours" in parsed_body:
                wedhours = parsed_body["wedhours"][0]
            else:
                wedhours = None

            if "thurhours" in parsed_body:
                thurhours = parsed_body["thurhours"][0]
            else:
                thurhours = None

            if "frihours" in parsed_body:
                frihours = parsed_body["frihours"][0]
            else:
                frihours = None      

            if "sathours" in parsed_body:
                sathours = parsed_body["sathours"][0]
            else:
                sathours = None

            db.replaceEmployeeByID(id, name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours)
            employee = db.getEmployeeByID(id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps(employee), "utf-8"))
        else:
            self.handle404()

#          PATCH

#   PATCH(employee by id)
    def handlePatchEmployeeByID(self, id):
        if "userID" not in self.sessionData:
            print("User not logged in")
            self.send_response(401)
            self.end_headers()
            return
        db = database.LabbieDB()
        employee = db.getEmployeeByID(id)
        print("    EMPLOYEE ----------->", employee)

        
        if employee:

            length = int(self.headers["Content-Length"])
            request_body = self.rfile.read(length).decode("utf-8") # opposite of bytes() function from line 21
            print("    raw body ----------->", request_body)
            
            parsed_body = parse_qs(request_body) # IMPORT
            print("    parsed body -------->", parsed_body)

            if "name" in parsed_body:
                name = parsed_body["name"][0]
            else:
                name = "____"

            if "shiftcolor" in parsed_body:
                shiftcolor = parsed_body["shiftcolor"][0]
            else:
                shiftcolor = "#FFFFFF"

            db.patchEmployeeByID(id, name, shiftcolor)
            employee = db.getEmployeeByID(id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(bytes(json.dumps(employee), "utf-8"))
        else:
            self.handle404()
        
#          404

#   404()
    def handle404(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not found.", "utf-8"))

#          DO's

    def do_OPTIONS(self):
        self.load_session()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, PUT, OPTIONS, PATCH")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.load_session()
        print("REQUEST ------------>", self.path)

        # PATH PARSING
        # /employees/1
        # ["", "employees", "1"]
        pathParts = self.path.split("/")[1:]
        collection = pathParts[0]
        if len(pathParts) > 1:
            member = pathParts[1]
        else: 
            member = None

        # ROUTING
        if collection == "employees":
            if member:
                self.handleGetEmployeeByID(member)
            else:
                self.handleGetEmployees()
        elif collection == "sessions":
            if member:
                self.handle404()
            else:
                self.handleGetSessions()
        else:
            self.handle404()

    def do_POST(self):
        self.load_session()
        print("REQUEST ------------>", self.path)

        # PATH PARSING
        pathParts = self.path.split("/")[1:]
        collection = pathParts[0]
        if len(pathParts) > 1:
            member = pathParts[1]
        else: 
            member = None
        
        # ROUTING
        if collection == "employees":
            if member:
                self.handle404()
            else:   
                self.handlePostEmployee()
        elif collection == "users":
            if member:
                self.handle404()
            else:
                self.handlePostUser()
        elif collection == "sessions":
            self.handleAuthenticateUser()
            # respond 201 == success, 401 == failure
        else:
            self.handle404()

    def do_DELETE(self):
        self.load_session()
        print("REQUEST ------------>", self.path)

        # PATH PARSING
        pathParts = self.path.split("/")[1:]
        collection = pathParts[0]
        if len(pathParts) > 1:
            member = pathParts[1]
        else: 
            member = None
        
        # ROUTING
        if collection == "employees":
            if member:
                self.handleDeleteEmployeeByID(member)
            else:   
                self.handle404()
        if collection == "sessions":
            if member:
                self.handle404()
            else:
                self.handleLogoutUser()
        else:
            self.handle404()

    def do_PUT(self):
        self.load_session()
        print("REQUEST ------------>", self.path)

        # PATH PARSING
        pathParts = self.path.split("/")[1:]
        collection = pathParts[0]
        if len(pathParts) > 1:
            member = pathParts[1]
        else: 
            member = None
        
        # ROUTING
        if collection == "employees":
            if member:
                self.handleReplaceEmployeeByID(member)
            else:   
                self.handle404()
        else:
            self.handle404()

    def do_PATCH(self):
        self.load_session()
        print("REQUEST ------------>", self.path)

        # PATH PARSING
        pathParts = self.path.split("/")[1:]
        collection = pathParts[0]
        if len(pathParts) > 1:
            member = pathParts[1]
        else: 
            member = None
        
        # ROUTING
        if collection == "employees":
            if member:
                self.handlePatchEmployeeByID(member)
            else:   
                self.handle404()
        else:
            self.handle404()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass # no implementation

def run():
    db = database.LabbieDB()
    db.createEmployeesTable()
    db.createUsersTable()
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = ThreadedHTTPServer(listen, MyRequestHandler)
    print("The server is now running!")
    server.serve_forever()

run()
