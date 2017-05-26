import json
import sqlite3
from enum import Enum
import os
from pybedtools import BedTool
import os
#from app import models

class Database():
    def __init__(self):
        path = os.path.dirname(os.path.dirname(__file__))
        print(path)
        #self.primers = path + '/resources/primers.db'
        self.primers = '/home/dnamdp/wc/SDGSPrimers/resources/primers.db'
        print self.primers
        self.primers_conn = sqlite3.connect(self.primers,check_same_thread=False)

    def query_db(self,c, query, args=(), one=False):
        """

        general method to do a select statement and format result into an easy to use dict

        :param c:
        :param query:
        :param args:
        :param one:
        :return: list of dicts
        """
        c.execute(query, args)
        r = [dict((c.description[i][0], value) \
                  for i, value in enumerate(row)) for row in c.fetchall()]
        return (r[0] if r else None) if one else r

    def __del__(self):
        self.primers_conn.commit()
        self.primers_conn.close()



class Users(Database):
    def query_db(self, c, query, args=(), one=False):
        return Database.query_db(self, c, query, args, one)

    def get_users(self):
        # pp = self.panelpal_conn.cursor()
        # users = self.query_db(pp,"SELECT * FROM users")
        # return users
        #print models.Users.query.all()
        pass

    def add_user(self,user, admin):
        pp = self.primers_conn.cursor()
        try:
            print user
            pp.execute("INSERT OR IGNORE INTO users(username,admin) VALUES (?,?)", (user,admin))
            self.primers_conn.commit()
            return pp.lastrowid
        except self.primers_conn.Error as e:
            self.primers_conn.rollback()
            print e.args[0]
            return -1