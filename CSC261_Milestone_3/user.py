from flask_login import UserMixin
class Users(UserMixin):
    def __init__(self, tup):
        self.tup = tup
        
    def get_id(self):
        return self.tup[0]

 