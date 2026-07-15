REPORT z_test_04.

DATA: lt_vbak TYPE TABLE OF vbak,
      lt_vbap TYPE TABLE OF vbap.

START-OF-SELECTION.

PERFORM load_sales.

FORM load_sales.

SELECT *
FROM vbak
INTO TABLE lt_vbak
.

SELECT *
FROM vbap
INTO TABLE lt_vbap
WHERE vbeln IN ( SELECT vbeln FROM vbak )
.

ENDFORM.