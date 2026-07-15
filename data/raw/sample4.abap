REPORT z_sales_analysis_single.

TABLES: vbak,
        vbap,
        kna1.

DATA: lv_vbeln TYPE vbak-vbeln,
      lv_kunnr TYPE kna1-kunnr,
      lv_name  TYPE kna1-name1.

START-OF-SELECTION.

PERFORM get_header_data.
PERFORM get_item_data.


*---------------------------------------------------------------------*
* FORM GET_HEADER_DATA
*---------------------------------------------------------------------*
FORM get_header_data .

SELECT SINGLE vbeln erdat kunnr
FROM vbak
INTO (lv_vbeln, sy-datum, lv_kunnr)
WHERE vbeln = lv_vbeln
.

CALL FUNCTION 'BAPI_SALESORDER_GETSTATUS'
  EXPORTING
    salesdocument = lv_vbeln
  IMPORTING
    status        = DATA(lv_status)
.

ENDFORM.


*---------------------------------------------------------------------*
* FORM GET_ITEM_DATA
*---------------------------------------------------------------------*
FORM get_item_data.

SELECT SINGLE posnr matnr
FROM vbap
INTO (DATA(lv_posnr), DATA(lv_matnr))
WHERE vbeln = lv_vbeln
.

PERFORM process_single_item.

ENDFORM.


*---------------------------------------------------------------------*
* FORM PROCESS_SINGLE_ITEM
*---------------------------------------------------------------------*
FORM process_single_item.

SELECT SINGLE kunnr name1
FROM kna1
INTO (lv_kunnr, lv_name)
WHERE kunnr = lv_kunnr
.

WRITE: / lv_kunnr, lv_name.

ENDFORM.