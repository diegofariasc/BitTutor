
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
CREATE TABLE FILE_RESOURCE (    name            VARCHAR(767)    NOT NULL,
                                course          INTEGER         NOT NULL,
                                title           VARCHAR(255)    NOT NULL,
                                format          VARCHAR(30)     NOT NULL DEFAULT "file",
                                location        TINYINT         NOT NULL,
                                description     MEDIUMTEXT,

                        CONSTRAINT validFormat  CHECK ( format = 'pdf' OR
                                                        format = 'swf' OR
                                                        format = 'youtube' OR
                                                        format = 'link' OR
                                                        format = 'image' OR
                                                        format = 'file' ),

                        FOREIGN KEY (course) REFERENCES COURSE (id),
                        PRIMARY KEY (name, course) );