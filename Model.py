import mysql.connector
import http.server
import socketserver
import time
from os import mkdir, walk, remove
from os.path import isdir
from shutil import rmtree
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from EmailNotifier import EmailNotifier


class BitTutorModel:

    # Constructor method
    def __init__( self ):

        self.__connection = mysql.connector.connect(    user="root", 
                                                        password="password", 
                                                        host="127.0.0.1",
                                                        database="BitTutor"  )

        self.__emailNotifier = EmailNotifier()


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



    # -----------------------------------------------------------------
    # DB ENTRY CREATION METHODS
    # -----------------------------------------------------------------

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
            categoryTuple = ( name, description )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, categoryTuple )
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
    def createCourse( self, teacherId, name, duration, language, lowAgeRange, upAgeRange, category, description, image, imageExtension ):

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
            instruction = "INSERT INTO COURSE (id, name, duration, language, lowAgeRange, upAgeRange, category, reports, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            courseTuple = ( id, name, duration, language, lowAgeRange, upAgeRange, category, 0, description )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, courseTuple )

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
            resourceTuple = ( name, course, title, format, inPageLocation, description )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, resourceTuple )
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
    The method creates a DB entry to denote that a user wishes to take a course 
    Input:  user(int), course(int) ids from user and wished course
    Output: (bool) whether the wishing flag insertion proceeded or not
    """
    def addToWishList( self, user, course ):

        try:

            # Prepare instruction
            instruction = "INSERT INTO WISHES ( user, course ) VALUES (%s, %s)"
            newTuple = ( user, course )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, newTuple )
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
    The method creates a DB entry to denote that a user subscribes into a course
    Input:  user(int), course(int) ids from user and wished course
    Output: (bool) whether the wishing flag insertion proceeded or not
    """
    def subscribe( self, user, course ):

        try:

            # Prepare instruction
            instruction = "INSERT INTO SUBSCRIBES ( user, course ) VALUES (%s, %s)"
            newTuple = ( user, course )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, newTuple )
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
    The method creates a DB entry to denote user banning 
    Input:  user(int), course(int) ids from user and course it is being banned from
    Output: (bool) whether the banning flag insertion proceeded or not
    """
    def banUserFromCourse( self, user, course ):

        try:

            # Prepare instruction
            instruction = "INSERT INTO IS_BANNED ( user, course ) VALUES (%s, %s)"
            newTuple = ( user, course )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, newTuple )
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
    The method creates a DB entry to denote user has already accessed a resource
    Input:  resourceName(str), user(int), course(int) ids from user and course it 
            is being accessed
    Output: (bool) whether the access flag insertion proceeded or not
    """
    def markResourceAsAccessed( self, resourceName, courseId, userId ):

        try:

            # Prepare instruction
            instruction = "INSERT INTO HAS_ACCESSED ( resourceName, course, user ) VALUES (%s, %s, %s)"
            newTuple = ( resourceName, courseId, userId )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, newTuple )
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
    The method creates a DB entry with a review
    Input:  author(int), course(int) ids from user and course being reviewed 
            stars(int) the number of stars given, comments(str) user comments
    Output: (bool) whether the review insertion proceeded or not
    """
    def addReview( self, author, course, stars, comments=None ):

        try:

            # Prepare instruction
            instruction = "INSERT INTO REVIEWS ( author, course, comments, stars ) VALUES (%s, %s, %s, %s)"
            reviewTuple = ( author, course, comments, stars )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, reviewTuple )
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
    Output: (bool) whether the mark insertion proceeded or not
    """
    def markCourseAsCompleted( self, user, course ):

        try:

            # Get current date
            currentDate = datetime.now()

            # Prepare instruction
            instruction = "INSERT INTO COMPLETES ( user, course, date ) VALUES (%s, %s, %s)"
            newTuple = ( user, course, currentDate.strftime('%Y-%m-%d') )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, newTuple )
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
    The method creates a new quiz in the DB
    Input:  course(int), title(str), instructions(str) with
            the quiz data. 
    Output: (bool) whether the quiz insertion proceeded or not
    """
    def createQuiz( self, course, title, instructions=None ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ title, instructions ] ):
                return False

            # Generation of a new id:
            # Query largest id in DB
            id = None
            cursor = self.__connection.cursor()
            query = "SELECT MAX(id) FROM QUIZ"
            cursor.execute( query )
            result = cursor.fetchall()

            # Check if no insertions yet. 
            # If so, assign id 1. Otherwise assign largest id + 1
            if ( result[0][0] == None ):
                id = 1
            else:
                id = result[0][0] + 1

            # If data is safe and a new id was created, then define data to insert into database
            instruction = "INSERT INTO QUIZ (id, course, title, instructions ) VALUES (%s, %s, %s, %s)"
            userTuple = ( id, course, title, instructions )

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
    The method creates a new question for a quiz in the DB
    Input:  quizId(int), instruction(str), 
            correct(str), optionAtext(str), optionBtext(str), 
            optionCtext(str), optionDtext(str)
    Output: (bool) whether the question insertion proceeded or not
    """
    def createQuestion( self, quizId, questionInstruction, correct, optionAtext, optionBtext, optionCtext, optionDtext ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ questionInstruction, optionAtext, optionBtext, optionCtext, optionDtext ] ):
                return False

            # Generation of a new id:
            # Query largest id in DB
            number = None
            cursor = self.__connection.cursor()
            query = "SELECT MAX(number) FROM QUESTION WHERE quizId = " + str(quizId)
            cursor.execute( query )
            result = cursor.fetchall()

            # Check if no insertions yet. 
            # If so, assign id 1. Otherwise assign largest id + 1
            if ( result[0][0] == None ):
                number = 1
            else:
                number = result[0][0] + 1

            # If data is safe and a new id was created, then define data to insert into database
            instruction = "INSERT INTO QUESTION ( number, quizId, instruction, correct, optionAtext, optionBtext, optionCtext, optionDtext ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            questionTuple = ( number, quizId, questionInstruction, correct, optionAtext, optionBtext, optionCtext, optionDtext )

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction, questionTuple )
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
    The method creates a DB entry to denote a user result on a quiz.
    Note: In case there is already a result for the given quiz the method overwrites it
    Input:  quizId(int), user(int) ids from user and quiz result is being registered on, 
            correctAnswers(int) result of the user
    Output: (bool) whether the result insertion proceeded or not
    """
    def registerQuizResult( self, quizId, user, correctAnswers ):

        try:

            # Remove existing result
            instruction = ("DELETE FROM GETS_RESULT WHERE quizId = %s AND user = %s") % (quizId,user)
            cursor  = self.__connection.cursor()
            cursor.execute( instruction )

            # Prepare instruction
            instruction = "INSERT INTO GETS_RESULT ( quizId, user, correctAnswers ) VALUES (%s, %s, %s)"
            newTuple = ( quizId, user, correctAnswers )

            # Execute and commit
            cursor.execute( instruction, newTuple )
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
    The method allows to remove an user and all its dependencies on the DB and the FS
    Input:  id(int) with user id
    Output: (bool) whether the resource insertion proceeded or not
    """
    # -----------------------------------------------------------------
    # DB ENTRY DELETION METHODS
    # -----------------------------------------------------------------


    def deleteUser( self, id ):

        try: 

            # Extract user course dependencies
            cursor = self.__connection.cursor()
            query = "SELECT * FROM TEACHES where user = " + str(id) 
            cursor.execute( query )
            result = cursor.fetchall()

            # Prepare instruction for user deletion
            instruction = "DELETE FROM USER WHERE id = " + str(id)

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction )
            self.__connection.commit()

            # Apply changes on FS
            userPath = self.__getUserPath( id )
            rmtree(userPath)

            # Removing all teaching courses
            for course in result:

                coursePath = self.__getCoursePath( course[1] )
                rmtree(coursePath)

            # Successful operation
            cursor.close()
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            cursor.close()
            return False            


    """
    The method allows to remove a course and all its dependencies on the DB and the FS
    Input:  id(int) with user id
    Output: (bool) whether the resource insertion proceeded or not
    """
    def deleteCourse( self, id ):

        try:

            # Prepare instruction
            instruction = "DELETE FROM COURSE WHERE id = " + str(id)

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction )
            self.__connection.commit()

            # Apply changes on FS
            coursePath = self.__getCoursePath( id )
            rmtree(coursePath)

            # Successful operation
            cursor.close()
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            cursor.close()
            return False


    """
    The method allows to remove a user subscription from a course
    Input:  user(int), course(int) with user and id
    Output: (bool) whether the resource insertion proceeded or not
    """
    def unsubscribe( self, user, course ):

        try:

            # Prepare instruction
            instruction = "DELETE FROM SUBSCRIBES WHERE user = " + str(user) + " AND course = " + str(course)

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction )
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
    The method allows to remove a course from a user's wish list
    Input:  user(int), course(int) with user and id
    Output: (bool) whether the resource insertion proceeded or not
    """
    def removeFromWishList( self, user, course ):

        try:

            # Prepare instruction
            instruction = "DELETE FROM WISHES WHERE user = " + str(user) + " AND course = " + str(course)

            # Execute and commit
            cursor  = self.__connection.cursor()
            cursor.execute( instruction )
            self.__connection.commit()

            # Successful operation
            cursor.close()
            return True

        except:

            # On rejection -> rollback
            self.__connection.rollback()
            cursor.close()
            return False


    # -----------------------------------------------------------------
    # DB INFORMATION RECOVERY METHODS
    # -----------------------------------------------------------------

    """
    The method allows to retrieve a user's id given its email adress
    Input:  mail (str) with user's adress
    Output: None (if not found) and (int) if found
    """
    def getUserIdFromEmail( self, mail ):

        try:

            cursor  = self.__connection.cursor()
            query   = "SELECT id FROM USER WHERE mail = '" + mail + "'"
            cursor.execute( query )

            return cursor.fetchall()[0][0]

        except:
            cursor.close()
            return None



    """
    The method allows to retrieve a user's id given its id
    Input:  id(int) with the user id
    Output: None (if not found) and (str) if found with user's full name
    """
    def getUserFullName( self, id ):

        try:

            cursor  = self.__connection.cursor()
            query   = "SELECT name FROM USER WHERE id = '" + str( id ) + "'"
            cursor.execute( query )

            return cursor.fetchall()[0][0]

        except:
            cursor.close()
            return None



    """
    The method allows to verify a users identity given its mail and password
    Input:  userMail(str) and password (str) with the user login data
    Output: None (if not found) and (str) if found with user's full name
    """
    def authenticateUser( self, userMail, password ):

        try:

            cursor  = self.__connection.cursor()
            query   = ("SELECT name FROM USER WHERE mail = '%s' AND password = '%s' ") % (userMail, password)
            cursor.execute( query )

            return cursor.fetchall()[0][0]

        except:
            cursor.close()
            return None



    """
    The method allows to extract a course title given its id
    Input:  courseId(int) with the course's id number
    Output: None (if not found) and (str) if found with course's name
    """
    def getCourseTitle( self, courseId ):

        try:

            cursor  = self.__connection.cursor()
            query   = ("SELECT name FROM COURSE WHERE id = '%s'") % (courseId)
            cursor.execute( query )

            return cursor.fetchall()[0][0]

        except:
            cursor.close()
            return None



    """
    The method allows to extract a course image from FS given its id
    Input:  courseId(int) with the course's id number
    Output: None (if not found) and (bytes) if found with the image
    """
    def getCourseImage( self, courseId ):

        try:

            # Find image by iteration as the extension is unknown
            for _, _, files in walk(self.__getCoursePath( courseId )):
                for file in files:

                    # Check if found already
                    if ( file.startswith("courseimg.") ):

                        # If so, load bytes and return them
                        imgPointer = open( self.__getCoursePath( courseId ) + file + "", 'rb')
                        content = imgPointer.read()
                        imgPointer.close()

                        return content

            return None

        except:

            return None



    """
    The method allows to extract an user's profile image from FS given its id
    Input:  userId(int) with the user's id number
    Output: None (if not found) and (bytes) if found with the image
    """
    def getUserImage( self, userId ):

        try:

            # Find image by iteration as the extension is unknown
            for _, _, files in walk(self.__getUserPath( userId )):
                for file in files:

                    # Check if found already
                    if ( file.startswith("profileimg.") ):

                        # If so, load bytes and return them
                        imgPointer = open( self.__getUserPath( userId ) + file + "", 'rb')
                        content = imgPointer.read()
                        imgPointer.close()

                        return content

            return None

        except:

            return None



    """
    The method allows to extract a category's image from FS given its name
    Input:  name(str) with the category name
    Output: None (if not found) and (bytes) if found with the image
    """    
    def getCategoryImage( self, name ):

        try:

            # Find image by iteration as the extension is unknown
            for _, _, files in walk(self.__getCategoryPath( name )):
                for file in files:

                    # Check if found already
                    if ( file.startswith("categoryimg.") ):

                        # If so, load bytes and return them
                        imgPointer = open( self.__getCategoryPath( name ) + file + "", 'rb')
                        content = imgPointer.read()
                        imgPointer.close()

                        return content

            return None

        except:

            return None


    """
    The method provides the courses offered for a particular user in a given 
    category. The method already considerates the non-inclusion of 
    already completed courses, suscribed courses, teaching courses,
    banned-from courses, and the age range indicated by the instructor.
    Input:  category(str) with the category to search on and userId(int) with the user id
    Output: (list) of tuples with all courses that are appearing in the wish list
            in the form (id, name, duration, language, lowAgeRange, upAgeRange, 
            category, reports, description, stars, teacher)
    Note:   The result is ordered by stars
    """
    def getUserCourseOfferOnCategoryForUser( self, category, userId ):

        try:

            cursor  =   self.__connection.cursor()
            query   =   ("SELECT * FROM \n" +\
                        "(\n" +\
                        "SELECT * from COURSE \n"+\
                        "NATURAL JOIN \n" +\
                        "(\n" +\
                        "(SELECT id, NULL stars FROM COURSE WHERE id NOT IN (SELECT course FROM REVIEWS))\n"+\
                        "UNION \n" +\
                        "(SELECT course id, AVG(stars) stars FROM REVIEWS GROUP BY course )\n"+\
                        ") SUB\n" +\
                        ") COURSE \n"+
                        "NATURAL JOIN \n"+
                        "(SELECT user teacher, course id  FROM TEACHES) TEACHES \n" +\
                        "WHERE COURSE.category = '%s' AND \n" + \
                        "COURSE.id NOT IN (SELECT course FROM IS_BANNED WHERE IS_BANNED.user = %s) AND \n" +\
                        "COURSE.id NOT IN (SELECT course FROM TEACHES WHERE TEACHES.user = %s) AND \n" +\
                        "COURSE.id NOT IN (SELECT course FROM SUBSCRIBES WHERE SUBSCRIBES.user = %s) AND \n" +\
                        "COURSE.id NOT IN (SELECT course FROM COMPLETES WHERE COMPLETES.user = %s) AND \n" +\
                        "COURSE.lowAgeRange <= (SELECT age FROM USER WHERE id = %s) AND \n" +\
                        "COURSE.upAgeRange >= (SELECT age FROM USER WHERE id = %s)\n" +\
                        "ORDER BY stars DESC" \
                        ) % (category, userId, userId, userId, userId, userId, userId)

            cursor.execute( query )
            return cursor.fetchall()

        except:

            cursor.close()
            return None


    """
    The method provides the wishing list of the given user
    Input:  id(int) with the user id
    Output: (list) of tuples with all courses that are appearing in the wish list
            in the form (id, name, duration, language, lowAgeRange, upAgeRange, 
            category, reports, description, stars, teacher)
    Note:   The given result already includes stars for its showing in the wish list
    Note2:  The given list is already ordered by stars!
    """
    def getUserWishList( self, id ):

        try:

            cursor  =   self.__connection.cursor()
            query   =   ("SELECT * FROM \n" + \
                        "(\n" + \
                        "SELECT * from COURSE \n"+ \
                        "NATURAL JOIN \n" +\
                        "(\n" + \
                        "(SELECT id, NULL stars FROM COURSE WHERE id NOT IN (SELECT course FROM REVIEWS))\n"+ \
                        "UNION \n" + \
                        "(SELECT course id, AVG(stars) stars FROM REVIEWS GROUP BY course )\n"+ \
                        ") SUB\n" + \
                        ") COURSE \n" + \
                        "NATURAL JOIN \n"+ \
                        "(SELECT user teacher, course id  FROM TEACHES) TEACHES \n" + \
                        "WHERE COURSE.id IN ( SELECT course FROM WISHES WHERE user = %s ) \n" + \
                        "ORDER BY stars DESC") \
                        % ( id )

            cursor.execute( query )
            return cursor.fetchall()      

        except:
            cursor.close()
            return None 


    """
    The method recovers all courses that the given user is taking
    Input:  id(int) with the user id
    Output: (list) of tuples in the form (id, name, description, teacher)
            with the course data of all currently taking courses
    """
    def getCurrentlyTakingCoursesForUser( self, id ):

        try: 
            
            cursor  = self.__connection.cursor()
            query   = ( "SELECT id, name, description, teacher FROM \n" +\
                        "(COURSE NATURAL JOIN \n"+\
                        "(SELECT user teacher, course id  FROM TEACHES) TEACHES) \n"+\
                        "NATURAL JOIN \n" +\
                        "(SELECT course id FROM SUBSCRIBES WHERE user = %s) SUBSCRIBES \n" ) \
                        % ( id )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            cursor.close()
            return None


    """
    The method gets all courses being taught by a user whose id is given
    Input:  id(int) with the teacher id
    Output: (list) of tuples (courseId, name, description) with the course
            data of all taught courses
    """
    def getTeachingCourses( self, id ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT id, name, description FROM \n" +\
                        "COURSE NATURAL JOIN \n"+\
                        "(SELECT course id FROM TEACHES WHERE user = %s) TEACHES") \
                        % ( id )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            cursor.close()
            return None


    """
    The method returns a list of tuples in the form (courseId, name, teacher)
    with the courses completed by the given user's id
    Input:  id(int) of the user whose completed courses must be searched
    Output: (list) of tuples (courseId, name, teacher) with one for each
            completed course
    """
    def getCompletedCourses( self, id ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT id, name, teacher FROM \n" +\
                        "(COURSE NATURAL JOIN \n"+\
                        "(SELECT user teacher, course id  FROM TEACHES) TEACHES) \n"+\
                        "NATURAL JOIN \n" +\
                        "(SELECT course id FROM COMPLETES WHERE user = %s) COMPLETES \n" ) \
                        % ( id )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            return None


    """
    The method allows to recover the student list on a given course
    Input:  id(int) of the course
    Output: (list) of tuples in the form (userId, userFullName, mail)
    """
    def getStudentListForCourse( self, id ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT id, name, mail FROM USER \n" +\
                        "NATURAL JOIN \n" +\
                        "(SELECT user id, course FROM SUBSCRIBES) SUBSCRIBES\n" +\
                        "WHERE course = %s" ) \
                        % ( id )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            cursor.close()
            return None



    """
    The method recovers all categories in the DB returning a list of tuples in 
    the form (name, description)
    Input:  None
    Output  (list) of tuples with all categories stored in DB
    """
    def getCategories( self ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT * FROM CATEGORY" )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            cursor.close()
            return None



    """
    The method returns all the quizes a user can still access on a course 
    Input:  userId(int), courseId(int) with the user and the course whose availables
            quizzes must be searched
    Output: (list) of tuples with all available quizzes in the form (quizId, title, 
            instructions, totalQuestions)
    """
    def getQuizListForUserOnCourse( self, userId, courseId ):

        try:
            cursor  = self.__connection.cursor()
            query   =   ("SELECT id, title, instructions, totalAnswers FROM QUIZ \n" +\
                        "NATURAL JOIN \n" +\
                        "(SELECT quizId id, COUNT(*) totalAnswers FROM QUESTION GROUP BY quizId) TOTAL\n" +\
                        "WHERE course = %s AND \n"+\
                        "(totalAnswers > \n"
                        "(SELECT correctAnswers FROM GETS_RESULT WHERE quizId = id AND user = %s)) OR \n" +\
                        "(SELECT correctAnswers FROM GETS_RESULT WHERE quizId = id AND user = %s) IS NULL") \
                        % ( courseId, userId, userId )

            cursor.execute( query )
            return cursor.fetchall()

        except:
            cursor.close()
            return None



    """
    The method returns a list of tuples with all questions from a given quiz
    in the form (instruction, correct, Atext, Btext, Ctext, Dtext)
    Input:  quizId with the id of the quiz whose questions must be recovered
    Output: (list) of tuples with all the questions of the given quiz
    """
    def getQuizQuestionSet( self, quizId ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT instruction, correct, optionAtext, optionBtext, optionCtext, optionDtext "+\
                        "FROM QUESTION WHERE quizId = %s ORDER BY number ASC" ) \
                    % ( quizId )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            cursor.close()
            return None


    """
    The method returns a list of tuples in the form (name, title, 
    format, inPageLocation, description) with the resources for a given course
    Note: File must be loaded with following method
    Input:  course(int) id from the course whose resources must be recovered
    Output: (list) of tuples with all file resources on DB
    """
    def getResourceListFromCourse( self, course ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT name, title, format, inPageLocation, description "+\
                        "FROM FILE_RESOURCE WHERE course = %s ORDER BY inPageLocation ASC" ) \
                    % ( course )

            cursor.execute( query )

            return cursor.fetchall()

        except:
            cursor.close()
            return None    


    """
    The method returns the byte collection of a file resource in the FS
    Input:  resourceName(str), course(int) with the file name and the course id
    Output: (bytes) from the file resource in the FS
    """
    def getResourceForCourse( self, resourceName, course ):

        try:
            cursor  = self.__connection.cursor()
            query   = ( "SELECT name, title, format, inPageLocation, description "+\
                        "FROM FILE_RESOURCE WHERE name = '%s' AND course = %s" ) \
                    % ( resourceName, course )

            cursor.execute( query )
            resource = cursor.fetchall()[0]
            
            # Check if content must be loaded from FS
            if resource[2] in {'pdf','swf','image','txt','file'}:

                # Convert to list for appending
                resource = list( resource )

                # Load resource
                filePointer = open( self.__getCoursePath( course ) + "Content/" + resourceName , 'rb')
                content = filePointer.read()
                filePointer.close()

                # Append it to list and translate it again into tuple type
                resource.append( content )
                resource = tuple(resource)

            return resource

        except:
            cursor.close()
            return None


    """
    The method generates a certificate for a user on a completed course
    Input:  user(int), course(int) with course and user id on DB
    Output: (bytes) from the generated jpg diploma
    """
    def generateCertificate( self, user, course ):

        try:

            # Acquire the course title and user full name from DB
            courseTitle = self.getCourseTitle( course )
            userName = self.getUserFullName( user )

            # Extract completion date 
            cursor  = self.__connection.cursor()
            query   = ( "SELECT date "+\
                        "FROM COMPLETES WHERE user = '%s' AND course = %s" ) \
                    % ( user, course )
            cursor.execute( query )
            date = cursor.fetchall()[0][0]

            # Load background
            pattern = Image.open("CertificateBackground.png", "r").convert('RGBA') 
            W, _ = pattern.size

            # Draw platform description
            msg = "Online Educational Platform"
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Arial.ttf", 15)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,165), msg, (0,0,0,0),font=font)

            # Draw title
            msg = "Certificate of Completion"
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Georgia.ttf", 57)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,200), msg, (20,102,204,0),font=font)

            # Draw awarded to
            msg = "Awarded to"
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Georgia.ttf", 20)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,280), msg, (100,100,100,100),font=font)

            # Draw name
            msg = userName
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Georgia.ttf", 30)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,310), msg, (0,0,0,0),font=font)

            # Draw sucessfully completion
            msg = "For sucessfully completing the course:"
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Georgia.ttf", 18)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,400), msg, (100,100,100,100),font=font)

            # Draw next course title
            msg = courseTitle               # Copy course title
            splittedMsg = msg.split(" ")    # Split title into words
            msg = ""                        # Line to append
            counter = 0                     # Number of characters in line
            position = 430                  # Vertical position on image

            # Iterate over word collection
            for word in splittedMsg:

                # Calculate word length
                counter += len(word) 

                # If the line length has exceeded 30 chars
                if counter >= 30:

                    # Restart counter
                    msg += word
                    counter = 0

                    # Draw line of text
                    draw = ImageDraw.Draw(pattern,'RGBA')
                    font = ImageFont.truetype("Georgia.ttf", 20)
                    w, _ = draw.textsize(msg, font=font)
                    draw.text(((W-w)/2,position), msg, (0,0,0,0),font=font)
                    msg = ""
                    position += 25
                    
                # If not already 30 chars just add to current line
                else:
                    msg += word + " "

            # If there is still string to add to certificate
            if msg != "":
                draw = ImageDraw.Draw(pattern,'RGBA')
                font = ImageFont.truetype("Georgia.ttf", 20)
                w, _ = draw.textsize(msg, font=font)
                draw.text(((W-w)/2,position), msg, (0,0,0,0),font=font)

            # Draw awarded to
            msg = "Date: " + date.strftime("%B %d, %Y")
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Georgia.ttf", 18)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,position + 50), msg, (100,100,100,100),font=font)

            # Draw legend
            msg = "This certificate does not confer any type of academic credits nor academic revalidation" 
            draw = ImageDraw.Draw(pattern,'RGBA')
            font = ImageFont.truetype("Georgia.ttf", 11)
            w, _ = draw.textsize(msg, font=font)
            draw.text(((W-w)/2,590), msg, (100,100,100,100),font=font)

            # Save temporarily in the FS
            pattern = pattern.convert('RGB')
            fileName = self.__getUserPath(user) + "Certificate_" + str(int(round(time.time() * 1000))) + ".jpg"
            pattern.save( fileName ,quality=100, subsampling=0)

            # Load bytes from FS
            imgPointer = open(fileName, 'rb')
            content = imgPointer.read()
            imgPointer.close()

            # Remove temporary FS file
            remove(fileName)

            # Return bytes
            return content

        except:
            cursor.close()
            return None


    # -----------------------------------------------------------------
    # DB EDITING METHODS
    # -----------------------------------------------------------------

    """
    The method allows to increase the report counter of a given course.
    The method automatically notifies students upon deletion and erases
    the course if the number of reports is 15
    Input:  courseId(int) with the course to report
    Output: true or false (bool) with whether the course was reported or not
    """
    def raiseReport( self, courseId ):

        try:

            cursor  = self.__connection.cursor()
            query   = ( "SELECT name courseName, description, reports, teacherName FROM COURSE \n" +
                        "NATURAL JOIN \n" +
                        "(SELECT user teacher, course id FROM TEACHES) TEACHES \n" +
                        "NATURAL JOIN \n" +
                        "(SELECT name teacherName, id teacher FROM USER) USER \n" +\
                        "WHERE id = '%s'" ) % (courseId)
            cursor.execute( query )
            courseName, description, totalReports, teacher = cursor.fetchall()[0]

            # Delete course if reached the max number of reports
            if (totalReports == 15):

                # Retrieve student list and notify all students
                studentList = self.getStudentListForCourse(courseId)

                for _, name, mail in studentList:
                
                    self.__emailNotifier.sendCourseCancellationDueToReportsNotification(\
                        mail,name,courseName,description,teacher)

                # Delete course
                self.deleteCourse(courseId)

            else:

                totalReports += 1

                # Update report counter
                instruction = ( "UPDATE COURSE \n" +\
                                "SET reports = %s \n" +\
                                "WHERE id = %s") % ( totalReports, courseId )
                cursor  = self.__connection.cursor()
                cursor.execute( instruction )
                self.__connection.commit()

            return True

        except:
            cursor.close()
            return False     


    """
    Edit user full name in the DB
    Input:  id(int), newName(str) with the user id and its new value
    Output: (bool) whether the user data modification proceeded or not
    """
    def modifyUserName( self, id, newName ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ newName ] ):
                return False

            # If data is safe then change data
            instruction = "UPDATE USER SET name=%s WHERE id=%s"
            userTuple = ( newName, id )

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
    Edit user password in the DB
    Input:  id(int), newPassword(str) with the user id and its new value
    Output: (bool) whether the user data modification proceeded or not
    """
    def modifyUserPassword( self, id, newPassword ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ newPassword ] ):
                return False

            # If data is safe then change data
            instruction = "UPDATE USER SET password=%s WHERE id=%s"
            userTuple = ( newPassword, id )

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
    Edit user age in the DB
    Input:  id(int), newAge(int) with the user id and its new value
    Output: (bool) whether the user data modification proceeded or not
    """
    def modifyUserAge( self, id, newAge ):

        try:

            # If data is safe then change data
            instruction = "UPDATE USER SET age=%s WHERE id=%s"
            userTuple = ( newAge, id )

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
    Edit user study level in the DB
    Input:  id(int), newLevel(str) with the user id and its new value
    Output: (bool) whether the user data modification proceeded or not
    """
    def modifyUserStudyLevel( self, id, newLevel ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ newLevel ] ):
                return False

            # If data is safe then change data
            instruction = "UPDATE USER SET studyLevel=%s WHERE id=%s"
            userTuple = ( newLevel, id )

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
    Edit user description in the DB
    Input:  id(int), newDescription(str) with the user id and its new value
    Output: (bool) whether the user data modification proceeded or not
    """
    def modifyUserDescription( self, id, newDescription ):

        try:

            # Analize data for SQL code injections
            if self.__hasSQLInjection( [ newDescription ] ):
                return False

            # If data is safe then change data
            instruction = "UPDATE USER SET description=%s WHERE id=%s"
            userTuple = ( newDescription, id )

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
    The method allows to extract an user's profile image from FS given its id
    Input:  userId(int) with the user's id number
    Output: None (if not found) and (bytes) if found with the image
    """
    def modifyUserImage( self, userId, newImage=None, newImageExtension=None ):

        try:

            userPath = self.__getUserPath( userId )

            # Find image by iteration as the extension is unknown
            for _, _, files in walk(self.__getUserPath( userId )):
                for file in files:

                    # Check if found already
                    if ( file.startswith("profileimg.") ):

                        # Remove current image if exists
                        remove( userPath  + file )
                                    
            # If provided new image
            if ( newImage != None ):
                imgPointer = open( userPath + "profileimg." + newImageExtension, 'wb')
                imgPointer.write( newImage )
                imgPointer.close()


            return True

        except:
            return False

