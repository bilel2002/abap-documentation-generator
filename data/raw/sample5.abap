REPORT z_test_01 .

DATA: lt_vbak TYPE TABLE OF vbak.

START-OF-SELECTION.

PERFORM get_data.

FORM get_data .
SELECT *
FROM
vbak
INTO TABLE lt_vbak
WHERE erdat = sy-datum
.
PERFORM process_data
.
ENDFORM.

FORM process_data.
WRITE: / 'DONE'.
ENDFORM.