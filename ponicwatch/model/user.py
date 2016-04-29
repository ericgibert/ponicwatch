import sys

class User(object):
    def __init__(self, db, login=None, password=None):
        self.db = db
        self.user_id, self.login, self.email, self.authorization, self.password, self.name = None, None, None, None, None, None  # unknown user
        if login and password:
            self.get_user(login, password)

    def get_user(self, login, password):
        """
        Fetch one record in tb_user matching the given parameters
        Convention: the controller itself must have the user_id = 1 and its login is 'ctrl'  --> secure access to add later
        :param name: tb_user.name
        :param password: tb_user.password --> to do: provide password encryption
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("SELECT * from tb_user where login=? and password=?", (login, password))
                user_row = curs.fetchall()
                if len(user_row) == 1:
                    self.user_id, self.login, self.email, self.authorization, self.password, self.name = user_row[0]
            finally:
                curs.close()

    def __str__(self):
        return "{}".format(self.name)