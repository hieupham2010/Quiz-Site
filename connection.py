import pymysql
from configdb import database as db
def executeQueryValNonData(query , val):
    try:
        connection = pymysql.connect(db['host'] , db['username'] , db['password'] , db['dbname'])
        cursor = connection.cursor()
        cursor.execute(query, val)
        cursor.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(e)
        return False

def executeQueryData(query):
    try:
        connection = pymysql.connect(db['host'] , db['username'] , db['password'] , db['dbname'])
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data
    except Exception as e:
        print(e)
        return False

def executeQueryValData(query , val):
    try:
        connection = pymysql.connect(db['host'] , db['username'] , db['password'] , db['dbname'])
        cursor = connection.cursor()
        cursor.execute(query, val)
        data = cursor.fetchall()
        cursor.close()
        return data
    except Exception as e:
        print(e)
        return False