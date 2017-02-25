import os
import time

g_adsl_account = {"name": "name",
                "username": "username",
                "password": "password"}
 
     
class Adsl:
    def __init__(self):
        self.name = g_adsl_account["name"]
        self.username = g_adsl_account["username"]
        self.password = g_adsl_account["password"]
 
    def set_adsl(self, account):
        self.name = account["name"]
        self.username = account["username"]
        self.password = account["password"]
 
    def connect(self):
        cmd_str = "rasdial %s %s %s" % (self.name, self.username, self.password)
        os.system(cmd_str)
        time.sleep(3)
 
        
    def disconnect(self):
        cmd_str = "rasdial %s /disconnect" % self.name
        os.system(cmd_str)
        time.sleep(3)
 
    def reconnect(self):
        self.disconnect()
        self.connect()

if __name__ == '__main__':
    adsl = Adsl()
    adsl.reconnect()