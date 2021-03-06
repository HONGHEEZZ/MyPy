CREATE TABLE JAVA_CODE_REPLACE_DETAIL
( FILE_NAME VARCHAR2(100),
TYPE VARCHAR2(100),
VAR_ID VARCHAR2(500),
VAR_VALUE_SEQ NUMBER,
VAR_VALUE VARCHAR2(1000),
VAR_LEFT_SPACE_LEN NUMBER,
VAR_RIGHT_LF_YN VARCHAR2(1),
TBL_ETC1 VARCHAR2(1000),
PRIMARY KEY (FILE_NAME, VAR_ID, VAR_VALUE_SEQ)
)
;

CREATE TABLE JAVA_CODE_REPLACE_LIST
( TARGET_DIV VARCHAR2(100),
SEQ NUMBER,
TYPE VARCHAR2(100),
VAR_ID VARCHAR2(100),
VAR_NAME VARCHAR2(1000),
VAR_DESC VARCHAR2(1000),
VAR_LEFT_SPACE_LEN NUMBER,
VAR_RIGHT_LF_YN VARCHAR2(1),
TBL_ETC1 VARCHAR2(1000),
PRIMARY KEY (TARGET_DIV, TYPE, SEQ, VAR_ID)
)
;


CREATE TABLE JAVA_FILE_IDEA
( TARGET_DIV VARCHAR2(100),
SEQ NUMBER,
TYPE VARCHAR2(100),
IDEA_DIR VARCHAR2(100),
IDEA_FILE_NAME VARCHAR2(100),
ORG_NAME VARCHAR2(100),
TBL_ETC1 VARCHAR2(100),
PRIMARY KEY (TARGET_DIV, TYPE, IDEA_DIR, IDEA_FILE_NAME)
)
;


CREATE TABLE JAVA_PG_DIR
( NO NUMBER,
LOC VARCHAR2(20),
DIR_ID VARCHAR2(50),
DIR_NAME VARCHAR2(50),
DIR_DIV VARCHAR2(50),
DIR_HOME VARCHAR2(200),
DIR_REST VARCHAR2(200),
NEED_COMMAND VARCHAR2(1),
COMMAND VARCHAR2(200),
WHERE_TO_SAVE VARCHAR2(200),
TBL_ETC1 VARCHAR2(200),
PRIMARY KEY (LOC, DIR_ID, DIR_DIV)
)
;


CREATE TABLE JAVA_PG_FILES
( NO NUMBER,
PG_ID VARCHAR2(200),
SEQ NUMBER,
TYPE VARCHAR2(200),
FILE_NAME VARCHAR2(200),
DIR VARCHAR2(200),
USE_YN VARCHAR2(1),
RUN_YN VARCHAR2(1),
TBL_ETC1 VARCHAR2(200),
PRIMARY KEY (PG_ID, FILE_NAME)
)
;


CREATE TABLE JAVA_PG_LIST (
NO NUMBER,
TARGET_DIV VARCHAR2(10),
PG_ID VARCHAR2(200),
PG_NAME VARCHAR2(200),
PG_DESC VARCHAR2(200),
SOURCE_TABLE VARCHAR2(200),
TARGET_TABLE_OWNER VARCHAR2(200),
TARGET_TABLE_ID VARCHAR2(200),
QUERY_FILE_DIR VARCHAR2(200),
QUERY_FILE VARCHAR2(200),
RUN_YN VARCHAR2(10),
TBL_ETC1 VARCHAR2(200),
PRIMARY KEY (PG_ID)
)
;



CREATE TABLE JAVA_TBL_COL_VAR
(
TABLE_NAME VARCHAR2(128),
T_COMMENTS VARCHAR2(1000),
SEQ NUMBER,
COLUMN_NAME VARCHAR2(128),
C_COMMENTS VARCHAR2(1000),
COL_VAR VARCHAR2(1000),
COL_MAP VARCHAR2(1000),
TBL_ETC1 VARCHAR2(1000),
TBL_ETC2 VARCHAR2(1000),
PRIMARY KEY (TABLE_NAME, COLUMN_NAME)
)
;


CREATE TABLE JAVA_TBL_SQL
( TABLE_NAME VARCHAR2(128),
SQL_DIV VARCHAR2(100),
SEQ NUMBER,
SQL VARCHAR2(1000),
TBL_ETC1 VARCHAR2(1000),
TBL_ETC2 VARCHAR2(1000),
PRIMARY KEY (TABLE_NAME, SQL_DIV, SEQ)
)
;
