
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