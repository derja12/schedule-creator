# import sqlite3
import os
import psycopg2
import psycopg2.extras
import urllib.parse

# def dict_factory(cursor, row):
#     d = {}
#     for i, col in enumerate(cursor.description):
#         d[col[0]] = row[i]
#     return d

class LabbieDB:

    def __init__(self):
        #self.connection = sqlite3.connect("labbie.db")
        #self.connection.row_factory = dict_factory
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()


    def createEmployeesTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS employees (id SERIAL PRIMARY KEY, name TEXT, totalhours INTEGER, shiftcolor TEXT, monhours TEXT, tuehours TEXT, wedhours TEXT, thurhours TEXT, frihours TEXT, sathours TEXT)")
        self.connection.commit()

    def createUsersTable(self):
        # self.cursor.execute("DROP TABLE users")
        # self.connection.commit()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, email TEXT, password TEXT, fName TEXT, lName TEXT)")
        self.connection.commit()
        
#                   GET EMPLOYEE

    def getEmployees(self):
        self.cursor.execute("SELECT * FROM employees")
        employees = self.cursor.fetchall()
        return employees

    def getEmployeeByID(self, employee_id):
        data = [employee_id]
        self.cursor.execute("SELECT * FROM employees WHERE id = %s", data)
        employee = self.cursor.fetchone()
        return employee

#                   GET USER by EMAIL

    def getUserByEmail(self, email):
        data = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = %s", data)
        user = self.cursor.fetchone()
        return user
        
#                   CREATE EMPLOYEE

    def createEmployee(self, name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours):
        data = [name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours]
        self.cursor.execute("INSERT INTO employees (name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", data)
        self.connection.commit()

#                   CREATE USER

    def createUser(self, email, password, fName, lName):
        data = [email, password, fName, lName]
        self.cursor.execute("INSERT INTO users (email, password, fName, lName) VALUES (%s,%s,%s,%s)", data)
        self.connection.commit()

#                   DELETE EMPLOYEE

    def deleteEmployeeByID(self,id):
        data = [id]
        self.cursor.execute("DELETE FROM employees WHERE id = %s", data)
        self.connection.commit()

#                   UPDATE EMPLOYEE

    def replaceEmployeeByID(self, id, name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours):
        data = [name, totalhours, shiftcolor, monhours, tuehours, wedhours, thurhours, frihours, sathours, id]
        self.cursor.execute("UPDATE employees SET name = %s, totalhours = %s, shiftcolor = %s, monhours = %s, tuehours = %s, wedhours = %s, thurhours = %s, frihours = %s, sathours = %s WHERE id = %s", data)
        self.connection.commit()

#                   PATCH EMPLOYEE

    def patchEmployeeByID(self, id, name, shiftcolor):
        data = [name, shiftcolor, id]
        self.cursor.execute("UPDATE employees SET name = %s, shiftcolor = %s where id = %s", data)
        self.connection.commit()

