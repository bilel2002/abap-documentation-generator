REPORT z_basic_select_test.

DATA: lv_kunnr TYPE kna1-kunnr,
      lv_name  TYPE kna1-name1.

START-OF-SELECTION.

PERFORM get_customer.

FORM get_customer.

  SELECT kunnr name1
    FROM kna1
    INTO (lv_kunnr, lv_name)
    WHERE kunnr = '0000000001'.

  WRITE: / lv_kunnr, lv_name.

ENDFORM.