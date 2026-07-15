REPORT z_
test_program.

DATA: lt_users TYPE TABLE OF usr02,
      ls_user  TYPE usr02.

SELECT      *     FROM usr02
INTO TABLE 
lt_users
WHERE bname = 'TESTUSER'


.


FORM get_data .
  PERFORM load_data USING lt_users.

ENDFORM.

FORM load_data.
  CALL FUNCTION 'BAPI_USER_GETDETAIL'
    EXPORTING
      username = ls_user-bname
    TABLES
      return = lt_users.

ENDFORM.