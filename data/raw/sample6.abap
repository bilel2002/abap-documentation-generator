REPORT z_test_02.

DATA: lv_kunnr TYPE kna1-kunnr.

START-OF-SELECTION.

PERFORM get_customer.

FORM get_customer.

SELECT  kunnr 
FROM kna1
INTO (lv_kunnr, DATA(lv_name))
WHERE kunnr = lv_kunnr
.

CALL
FUNCTION
'BAPI_CUSTOMER_GETDETAIL'
EXPORTING
customer = lv_kunnr
IMPORTING
name = lv_name
.

ENDFORM.