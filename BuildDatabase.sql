
-- Drop previous database constructions and re-build
DROP DATABASE IF EXISTS BitTutor;
CREATE DATABASE BitTutor;
USE BitTutor;

-- Category table
CREATE TABLE CATEGORY ( name            VARCHAR(255)    NOT NULL,
                        image           VARCHAR(1024)   NOT NULL,
                        description     MEDIUMTEXT      NOT NULL,

                        PRIMARY KEY (name) );

-- Course table
CREATE TABLE COURSE (   id              INTEGER         NOT NULL,
                        name            VARCHAR(1024)   NOT NULL,
                        image           VARCHAR(1024)   NOT NULL,
                        duration        INTEGER         NOT NULL,
                        language        VARCHAR(2)      NOT NULL,
                        lowAgeRange     TINYINT         NOT NULL, 
                        upAgeRange      TINYINT         NOT NULL, 
                        category        VARCHAR(255)    NOT NULL,
                        reports         TINYINT         NOT NULL,

                        CONSTRAINT validLanguage    CHECK ( language = 'es' OR
                                                            language = 'en' OR
                                                            language = 'de' OR
                                                            language = 'fr' OR
                                                            language = 'hi' OR
                                                            language = 'jv' OR
                                                            language = 'pt' OR
                                                            language = 'ru' OR
                                                            language = 'zh'),
                        CONSTRAINT minDuration      CHECK ( duration > 0 ),
                        CONSTRAINT minLowAgeRange   CHECK ( lowAgeRange > 0 ),
                        CONSTRAINT minUpAgeRange    CHECK ( upAgeRange > 0 ),
                        CONSTRAINT maxUpAgeRange    CHECK ( upAgeRange < 100 ),
                        CONSTRAINT validAgeRange    CHECK ( lowAgeRange <= upAgeRange ),
                        CONSTRAINT maxReportNum     CHECK ( reports <= 15 ),

                        FOREIGN KEY (category) REFERENCES CATEGORY (name),
                        PRIMARY KEY (id) );


-- User table
CREATE TABLE USER   (   id              INTEGER         NOT NULL,
                        mail            VARCHAR(255)    UNIQUE NOT NULL,
                        name            VARCHAR(255)    NOT NULL,
                        password        VARCHAR(30)     NOT NULL,
                        age             TINYINT         NOT NULL,
                        studyLevel      VARCHAR(10)     NOT NULL,
                        description     MEDIUMTEXT,
                        image           VARCHAR(1024),


                        CONSTRAINT validStudyLevel  CHECK ( studyLevel = 'elementary' OR
                                                            studyLevel = 'middle' OR
                                                            studyLevel = 'high' OR
                                                            studyLevel = 'bachelor' OR
                                                            studyLevel = 'master' OR
                                                            studyLevel = 'phd' ),

                        CONSTRAINT validUserAge     CHECK ( age > 0 AND age < 100 ),
                        PRIMARY KEY (id) );

-- File_resource table
CREATE TABLE FILE_RESOURCE (    name            VARCHAR(766)    NOT NULL,
                                course          INTEGER         NOT NULL,
                                title           VARCHAR(255)    NOT NULL,
                                format          VARCHAR(30)     NOT NULL DEFAULT "file",
                                inPageLocation  TINYINT         NOT NULL,
                                description     MEDIUMTEXT,

                        CONSTRAINT validFormat  CHECK ( format = 'pdf' OR
                                                        format = 'swf' OR
                                                        format = 'youtube' OR
                                                        format = 'link' OR
                                                        format = 'image' OR
                                                        format = 'txt' OR
                                                        format = 'file' ),

                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (name, course) );

-- Intermediate table between file_resource and user table
CREATE TABLE HAS_ACCESSED ( resourceName    VARCHAR(766)    NOT NULL,
                            course          INTEGER         NOT NULL,
                            user            INTEGER         NOT NULL,

                            FOREIGN KEY (resourceName) REFERENCES FILE_RESOURCE (name),
                            FOREIGN KEY (course) REFERENCES COURSE (id),
                            FOREIGN KEY (user) REFERENCES USER (id),
                            PRIMARY KEY (resourceName, course, user) );

-- Intermediate table between course and user table with suscribing relation
CREATE TABLE SUSCRIBES (user    INTEGER NOT NULL,
                        course  INTEGER NOT NULL,

                        FOREIGN KEY (user) REFERENCES USER (id),
                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (user,course) );

-- Intermediate table between course and user table with teaching relation
CREATE TABLE TEACHES (  user    INTEGER NOT NULL,
                        course  INTEGER NOT NULL,

                        FOREIGN KEY (user) REFERENCES USER (id),
                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (user,course) );

-- Intermediate table between course and user table with user banning relation
CREATE TABLE IS_BANNED (user    INTEGER NOT NULL,
                        course  INTEGER NOT NULL,

                        FOREIGN KEY (user) REFERENCES USER (id),
                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (user,course) );

-- Intermediate table between course and user table with completing relation
CREATE TABLE COMPLETES (user    INTEGER NOT NULL,
                        course  INTEGER NOT NULL,
                        date    DATE NOT NULL,

                        FOREIGN KEY (user) REFERENCES USER (id),
                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (user,course) );

-- Intermediate table between course and user table with reviewing relation
CREATE TABLE REVIEWS (  author      INTEGER NOT NULL,
                        course      INTEGER NOT NULL,
                        comments    MEDIUMTEXT,
                        stars       TINYINT NOT NULL,

                        CONSTRAINT validStars CHECK ( stars >= 1  AND stars <= 5 ),

                        FOREIGN KEY (author) REFERENCES USER (id),
                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (author,course) );

-- Quiz table
CREATE TABLE QUIZ ( id              INTEGER NOT NULL,
                    course          INTEGER NOT NULL,
                    title           VARCHAR(1024) NOT NULL,
                    instructions    MEDIUMTEXT,

                    FOREIGN KEY (course) REFERENCES COURSE (id),
                    PRIMARY KEY (id, course) );

-- Question table
CREATE TABLE QUESTION ( number          INTEGER NOT NULL,
                        quizId          INTEGER NOT NULL,
                        correct         VARCHAR(1) NOT NULL,
                        optionAtext     MEDIUMTEXT,
                        optionBtext     MEDIUMTEXT,
                        optionCtext     MEDIUMTEXT,
                        optionDtext     MEDIUMTEXT,
                        optionAimage    VARCHAR(1024),
                        optionBimage    VARCHAR(1024),
                        optionCimage    VARCHAR(1024),
                        optionDimage    VARCHAR(1024),
                        instruction     MEDIUMTEXT,    

                        CONSTRAINT validAnswer  CHECK ( correct = 'a' OR
                                                        correct = 'b' OR
                                                        correct = 'c' OR
                                                        correct = 'd' ),
                    
                        FOREIGN KEY (quizId) REFERENCES QUIZ (id),
                        PRIMARY KEY (number, quizId) );

-- Intermediate table between quiz and user table with getting result relation
CREATE TABLE GETS_RESULT (  quizId          INTEGER NOT NULL,
                            course          INTEGER NOT NULL,
                            user            INTEGER NOT NULL,
                            correctAnswers  INTEGER NOT NULL,

                            FOREIGN KEY (quizId) REFERENCES QUIZ (id),
                            FOREIGN KEY (course) REFERENCES COURSE (id),
                            FOREIGN KEY (user) REFERENCES USER (id),
                            PRIMARY KEY (quizId,course,user) );