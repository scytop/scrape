CREATE TABLE course (year CHAR(4), quarter CHAR(1), subject VARCHAR(100),
    name VARCHAR(255), tag VARCHAR(40), instructor VARCHAR(255), section CHAR(6));

LOAD DATA LOCAL INFILE 'records.txt' INTO TABLE course;
