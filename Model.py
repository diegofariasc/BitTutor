import mysql.connector
import http.server
import socketserver
from os import mkdir
from os.path import isdir
from datetime import datetime


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
    Method for getting the course's directory path in the file structure
    Input:  id (int) of the course
    Output: (str) with the course's directory path
    """
    def __getCoursePath( self, id ):
        return "Courses/" + str(id) + "/"


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
            
            if not isdir(categoryPath) :
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
    def createCourse( self, teacherId, name, duration, language, lowAgeRange, upAgeRange, category, image, imageExtension ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ name, language, category ] ):
                return False

            # Generation of a new id:
            # Query largest id in DB
            id = None
            cursor = self.__connection.cursor()
            query = "SELECT MAX(id) FROM COURSE"
            cursor.execute( query )
            result = cursor.fetchall()

            # Check if no insertions yet. 
            # If so, assign id 1. Otherwise assign largest id + 1
            if ( result[0][0] == None ):
                id = 1
            else:
                id = result[0][0] + 1

            # If data is safe and a new id was created, then define data to insert into database
            instruction = "INSERT INTO COURSE (id, name, duration, language, lowAgeRange, upAgeRange, category, reports) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            userTuple = ( id, name, duration, language, lowAgeRange, upAgeRange, category, 0 )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, userTuple )

            # Register course instructor
            instruction = "INSERT INTO TEACHES (user, course ) VALUES (%s, %s)"
            userTuple = ( teacherId, id )
            cursor.execute( instruction, userTuple )
            self.__connection.commit()

            # If commitment is successful reflect DB changes on FS structure
            coursePath = self.__getCoursePath(id)

            if not isdir(coursePath) :
                mkdir( coursePath )

            # Write image
            imgPointer = open( coursePath + "courseimg." + imageExtension, 'wb')
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

            if not isdir(userPath) :
                mkdir( userPath )

            # If needed write image
            if ( image != None ):
                imgPointer = open( userPath + "profileimg." + imageExtension, 'wb')
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
    The method allows to push a new resource into the course FS and DB
    Input:  name (str), course(int), format(str), inPageLocation(int)
            description=None(str), file=None(bytes), fileExtension=None(str) with
            the resource data. 
    Output: (bool) whether the resource insertion proceeded or not
    """
    def submitResource( self, name, course, title, format, inPageLocation, description, file=None ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ name, title, format, description ] ):
                return False

            # If data is safe then define data to insert into database
            instruction = "INSERT INTO FILE_RESOURCE ( name, course, title, format, inPageLocation, description ) VALUES (%s, %s, %s, %s, %s, %s)"
            userTuple = ( name, course, title, format, inPageLocation, description )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, userTuple )
            self.__connection.commit()

            # If commitment is successful reflect DB changes on FS structure
            resourcePath = self.__getCoursePath(course) + "Content/"

            if not isdir(resourcePath) :
                mkdir( resourcePath )
            

            # If needed write file
            if ( file != None ):
                imgPointer = open( resourcePath + name, 'wb')
                imgPointer.write( file )
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
    The method creates a DB entry to denote user banning 
    Input:  user(int), course(int) ids from user and course it is being banned from
    Output: (bool) whether the resource insertion proceeded or not
    """
    def banUserFromCourse( self, user, course ):

        try:

            # Prepare instruction
            instruction = "INSERT INTO IS_BANNED ( user, course ) VALUES (%s, %s)"
            userTuple = ( user, course )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, userTuple )
            self.__connection.commit()

            # Successful operation
            cursor.close()
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            cursor.close()
            return False


    """
    The method creates a DB entry to denote a course has been completed by an user
    Input:  user(int), course(int) ids from user and course being completed
    Output: (bool) whether the resource insertion proceeded or not
    """
    def markCourseAsCompleted( self, user, course ):

        try:

            # Get current date
            currentDate = datetime.now()

            # Prepare instruction
            instruction = "INSERT INTO COMPLETES ( user, course, date ) VALUES (%s, %s, %s)"
            userTuple = ( user, course, currentDate.strftime('%Y-%m-%d') )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, userTuple )
            self.__connection.commit()

            # Successful operation
            cursor.close()
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            cursor.close()
            return False

    # Get a user data given its id
    def getUserById( self, id ):


        cursor  = self.__connection.cursor()
        query   = "SELECT * FROM USER WHERE id =" + str( id )

        cursor.execute( query )

        return cursor[0]




