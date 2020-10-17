import mysql.connector
import http.server
import socketserver
from os import mkdir

class BitTutorModel:

    # Constructor method
    def __init__( self ):

        self.__connection = mysql.connector.connect(    user="root", 
                                                        password="password", 
                                                        host="127.0.0.1",
                                                        database="BitTutor"  )

    """
    Method for preventing SQL-injection attacks
    Input:  fields (list) with all attributes to insert in the DB
    Output: (bool) whether all attributes are safe or not
    """
    def __hasSQLInjection( self, fields ):

        for field in fields:

            if str( field ).__contains__(";"):
                return True

        return False


    """
    Method for getting the category's directory path in the file structure
    Input:  name (str) of the category
    Output: (str) with the category's directory path
    """
    def __getCategoryPath( self, name ):
        return "Categories/" + name + "/"


    """
    Method for getting the user's directory path in the file structure
    Input:  id (int) of the user
    Output: (str) with the user's directory path
    """
    def __getUserPath( self, id ):
        return "Users/" + str(id) + "/"


    """
    Create a new category in the database and in the file structure
    Input:  name (str), description=None(str), image=None(bytes), 
            imageExtension=None(str) with the category data. 
    Output: (bool) whether the category insertion proceeded or not
    """
    def createCategory( self, name, description, image=None, imageExtension=None ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ name, description ] ):
                return False

            # If data is safe , then define data to insert into database
            instruction = "INSERT INTO CATEGORY (name, description) VALUES (%s, %s)"
            userTuple = ( name, description )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, userTuple )
            self.__connection.commit()

            # If commitment is successful reflect DB changes on FS structure
            categoryPath = self.__getCategoryPath(name)
            mkdir( categoryPath )

            # If needed write image
            if ( image != None ):
                imgPointer = open( categoryPath + "categoryimg." + imageExtension, 'wb')
                imgPointer.write( image )
                imgPointer.close()

            # Successful operation
            cursor.close()
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            cursor.close()
            return False


    """
    Create a new user in the database and in the file structure
    Input:  mail (str), name (str), password(str), age(int), 
            studyLevel(str), description=None(str), image=None(bytes), imageExtension=None(str) with
            the user data. 
    Output: (bool) whether the user insertion proceeded or not
    """
    def createUser( self, mail, name, password, age, studyLevel, description=None, image=None, imageExtension=None ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ mail, name, password, age, studyLevel, description ] ):
                return False

            # Generation of a new id:
            # Query largest id in DB
            id = None
            cursor = self.__connection.cursor()
            query = "SELECT MAX(id) FROM USER"
            cursor.execute( query )
            result = cursor.fetchall()

            # Check if no insertions yet. 
            # If so, assign id 1. Otherwise assign largest id + 1
            if ( result[0][0] == None ):
                id = 1
            else:
                id = result[0][0] + 1

            # If data is safe and a new id was created, then define data to insert into database
            instruction = "INSERT INTO USER (id, mail, name, password, age, studyLevel, description) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            userTuple = ( id, mail, name, password, age, studyLevel, description )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, userTuple )
            self.__connection.commit()

            # If commitment is successful reflect DB changes on FS structure
            userPath = self.__getUserPath(id)
            mkdir( userPath )

            # If needed write image
            if ( image != None ):
                imgPointer = open( userPath + "profileimg." + imageExtension, 'wb')
                imgPointer.write( image )
                imgPointer.close()

            # Successful operation
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            return False



    # Get a user data given its id
    def getUserById( self, id ):


        cursor  = self.__connection.cursor()
        query   = "SELECT * FROM USER WHERE id =" + str( id )

        cursor.execute( query )

        return cursor[0]




