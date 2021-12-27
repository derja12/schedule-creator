import base64, os

class SessionStore:

    def __init__(self):
        self.sessions = {}

    # FOR createSession()
    def generateSessionId(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

    def createSession(self):
        sessionId = self.generateSessionId()
        self.sessions[sessionId] = {}
        return sessionId

    def getSessionData(self, sessionId):
        if sessionId in self.sessions:
            return self.sessions[sessionId]
        else:
            return None





    # |||          |||
    # VVV OPTIONAL VVV

    def storeSessionData(self, sessionId, data):
        pass

    def storeSessionUserId(self, sessionId, data):
        pass

    def clearSession(self, sessionId):
        pass

    def doesSessionExist(self, sessionId):
        pass

