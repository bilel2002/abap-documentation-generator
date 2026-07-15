REPORT Z_REPORT250 NO STANDARD PAGE HEADING LINE-SIZE
 128   MESSAGE-ID Z_INTERFACES.

*----------------------------------------------------------------------*
* Auteur : C. HAURIE HONTAS
*
*----------------------------------------------------------------------*
* Date de création : 25/09/2007                                        *
*----------------------------------------------------------------------*
* Système/Module :                                                     *
*                                                                      *
* TITRE :  Compta Engagement LOT 1                                     *
*----------------------------------------------------------------------*
* Référence du document de conception : Référencement Fournisseurs     *
* Comparaison des conditions d'achat commande/société/société          *
*----------------------------------------------------------------------*
* Définition :                                                         *
*----------------------------------------------------------------------*
* Modifications :                                                      *
***********************************************************************

TABLES :  EKKO, LFB1, LFM1, T161.

TYPE-POOLS: SLIS.

* Déclaration des paramètres nécessaires à la fonction ALV
DATA : WGT_FIELDCAT TYPE TABLE OF LVC_S_FCAT,
       OK_CODE LIKE SY-UCOMM,
       WGT_AFFICHE TYPE TABLE OF ZLISTE_250,
       WGS_AFFICHE TYPE ZLISTE_250,
       G_REPID LIKE SY-REPID,
       MYCONTAINER TYPE SCRFNAME VALUE 'CONTAINER',
* reference to custom container: neccessary to bind ALV Control
       CUSTOM_CONTAINER TYPE REF TO CL_GUI_CUSTOM_CONTAINER,
       GRID1  TYPE REF TO CL_GUI_ALV_GRID.
*.........................................................
* 'x_save' contains a flag to control which kind of layout the user
* can save (in this example it is set to 'A' for all layout types).
*
* Variables of type DISVARIANT identify a layout.
* When provided as parameter for 'set_grid_for_first_display',
* it must contain at least the report-id.
*
DATA: X_SAVE,  "for parameter I_SAVE: modus for saving a layout
      X_LAYOUT TYPE DISVARIANT,
      G_EXIT TYPE C.  "is set if the user has aborted a layout popup

* The variables 'def_layout' and 'spec_layout' are set during
* interactions on the selection screen.
* 'gs_variant' finally holds the chosen layout.

DATA: DEF_LAYOUT  TYPE DISVARIANT,     "default layout
      DEFAULT TYPE C VALUE ' ',
      GS_VARIANT   TYPE DISVARIANT.     "finally chosen layout

*DATA : BEGIN OF WGT_EKKO OCCURS 0,
*         EBELN LIKE EKKO-EBELN,
*         BUKRS LIKE EKKO-BUKRS,
*         BSTYP LIKE EKKO-BSTYP,
*         BSART LIKE EKKO-BSART,
*         ERNAM LIKE EKKO-ERNAM,
*         LIFNR LIKE EKKO-LIFNR,
*         ZTERM LIKE EKKO-ZTERM,
*         ZTERM1 LIKE EKKO-ZTERM,
*         VTEXT1 LIKE TVZBT-VTEXT,
*         ZTERM2 LIKE EKKO-ZTERM,
*         VTEXT2 LIKE TVZBT-VTEXT,
*         ZTERM3 LIKE EKKO-ZTERM,
*         VTEXT3 LIKE TVZBT-VTEXT,
*         EKORG LIKE EKKO-ZTERM,
*         BEDAT LIKE EKKO-BEDAT,
*       END OF WGT_EKKO.

DATA : BEGIN OF WGT_LFB1 OCCURS 0,
         LIFNR LIKE LFB1-LIFNR,
         EKORG LIKE LFB1-ZTERM,
       END OF WGT_LFB1.

DATA : BEGIN OF WGT_LFM1 OCCURS 0,
         LIFNR LIKE LFM1-LIFNR,
         EKORG LIKE LFM1-ZTERM,
       END OF WGT_LFM1.
DATA  BELNRMM.

DATA  W_EBELN LIKE RSEG-EBELN.
*----------------------------------------------------------------------*
* ECRAN DE SELECTION :
*----------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK PAS01 WITH FRAME TITLE TEXT-001.

SELECTION-SCREEN SKIP.

SELECT-OPTIONS : S_BEDAT FOR EKKO-BEDAT,  "date de commande
                 S_BSTYP FOR EKKO-BSTYP,  "catégorie de commande
                 S_BSART FOR EKKO-BSART, "type de commande
                 S_EKGRP FOR EKKO-EKGRP,  "groupe d'acheteurs
                 S_EKORG FOR EKKO-EKORG.  "organisation achat

SELECTION-SCREEN END OF BLOCK PAS01.

PARAMETER P_DEF TYPE C  DEFAULT 'X' NO-DISPLAY.

SELECTION-SCREEN BEGIN OF BLOCK VARI WITH FRAME TITLE TEXT-003.
PARAMETERS:  P_VARI    LIKE DISVARIANT-VARIANT.

SELECTION-SCREEN END OF BLOCK VARI.
************************************************************
************************************************************
* Predefine a local class for event handling to allow the
* declaration of a reference variable.
CLASS LCL_EVENT_RECEIVER DEFINITION DEFERRED.
*
************************************************************

DATA: EVENT_RECEIVER TYPE REF TO LCL_EVENT_RECEIVER.

* § Step 1. Define a (local) class for event handling

****************************************************************
* LOCAL CLASSES: Definition
****************************************************************
*===============================================================
* class c_event_receiver: local class to handle print events...
*    - PRINT_END_OF_PAGE (page footer)
*    - PRINT_TOP_OF_LIST (list header)
*
*----------------------------------------------------------------------*
* CLASS DEFINITION :
*----------------------------------------------------------------------*
CLASS LCL_EVENT_RECEIVER DEFINITION.

  PUBLIC SECTION.
* § 2. Define a method for each print event you need.
    METHODS:

    HANDLE_TOP_OF_LIST
        FOR EVENT PRINT_TOP_OF_LIST OF CL_GUI_ALV_GRID,

    HANDLE_END_OF_PAGE
        FOR EVENT PRINT_END_OF_PAGE OF CL_GUI_ALV_GRID.

  PRIVATE SECTION.
    DATA: PAGENUM TYPE I.

ENDCLASS.                    "lcl_event_receiver DEFINITION
*
* c_event_receiver (Definition)

*----------------------------------------------------------------------*
* CLASS IMPLEMENTATION :
*----------------------------------------------------------------------*
CLASS LCL_EVENT_RECEIVER IMPLEMENTATION.

*§ 3. Implement your event handler methods. Use WRITE to provide output.
*-------------------------------------------
  METHOD HANDLE_TOP_OF_LIST.
*    DATA: TABLENAME(30) TYPE C.
    CLEAR PAGENUM.
*    PERFORM GET_TABLENAME CHANGING TABLENAME.
    WRITE: / ' Saisie du: ',
            S_BEDAT-LOW, ' au ', S_BEDAT-HIGH.

    WRITE: / 'Catégories de document  : ',
            S_BSTYP-LOW, ' à ', S_BSTYP-HIGH.

    WRITE: / 'Types de document  : ',
            S_BSART-LOW, ' à ', S_BSART-HIGH.

    WRITE: / 'Groupes d acheteurs  : ',
            S_EKGRP-LOW, ' à ', S_EKGRP-HIGH.

    WRITE: / 'Organisation d achats : ',
            S_EKORG-LOW, ' à ', S_EKORG-HIGH.

  ENDMETHOD.                           "handle_top_of_list
*-----------------------------------------

*-------------------------------------------
  METHOD HANDLE_END_OF_PAGE.

    DATA: TABLENAME(30) TYPE C.

*    PERFORM GET_TABLENAME CHANGING TABLENAME.
    ADD 1 TO PAGENUM.
*    WRITE: /,'Event: PRINT_END_OF_PAGE'(003),
*             'Number of pages so far: '(004), PAGENUM.
    WRITE: /,'Page : '(R01), PAGENUM.
  ENDMETHOD.                           "handle_end_of_page

ENDCLASS.                    "lcl_event_receiver IMPLEMENTATION
*
*===================================================================
********************************************************************

* Controls are not integrated into the TAB-Order
* Call "set_focus" if you want to make sure that 'the cursor'
* is active in your control.
**  CALL METHOD CL_GUI_CONTROL=>SET_FOCUS EXPORTING CONTROL = GRID1.
* Control Framework flushes at the end of PBO automatically!
*----------------------------------------------------------------------*
* AT SELECTION-SCREEN OUTPUT :
*----------------------------------------------------------------------*
AT SELECTION-SCREEN OUTPUT.

  PERFORM R00_INIT_ZONES.

* The default layout is fetched the first time the PBO of the
* selection screen is called.
* If a default layout exist, its identification
* is saved in 'def_layout'.
*
  IF DEFAULT = ' '.
*    clear def_layout.
    MOVE G_REPID TO DEF_LAYOUT-REPORT.
    CALL FUNCTION 'LVC_VARIANT_DEFAULT_GET'
      EXPORTING
        I_SAVE     = X_SAVE
      CHANGING
        CS_VARIANT = DEF_LAYOUT
      EXCEPTIONS
        NOT_FOUND  = 2.
    IF SY-SUBRC = 2.
*      wgv_no_v = 'X'.
      EXIT.
    ELSE.
*     set name of layout on selection screen
      P_VARI = DEF_LAYOUT-VARIANT.
      DEFAULT = 'X'.
    ENDIF.
  ENDIF.                             "default IS INITIAL

*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*----------------------------------------------------------------------*
* AT SELECTION-SCREEN ON VALUE-REQUEST :
*----------------------------------------------------------------------*
AT SELECTION-SCREEN ON VALUE-REQUEST FOR P_VARI.

* popup F4 help to select a layout

  CLEAR X_LAYOUT.
  MOVE G_REPID TO X_LAYOUT-REPORT.

  CALL FUNCTION 'LVC_VARIANT_F4'
    EXPORTING
      IS_VARIANT = X_LAYOUT
      I_SAVE     = X_SAVE
    IMPORTING
      E_EXIT     = G_EXIT
      ES_VARIANT = DEF_LAYOUT
    EXCEPTIONS
      NOT_FOUND  = 1
      OTHERS     = 2.
  IF SY-SUBRC NE 0.
    MESSAGE ID SY-MSGID TYPE SY-MSGTY NUMBER SY-MSGNO
            WITH SY-MSGV1 SY-MSGV2 SY-MSGV3 SY-MSGV4.
  ELSE.
    IF G_EXIT NE 'X'.
* set name of layout on selection screen
      P_VARI    = DEF_LAYOUT-VARIANT.
    ENDIF.
  ENDIF.

*----------------------------------------------------------------------*
* AT SELECTION-SCREEN :
*----------------------------------------------------------------------*
AT SELECTION-SCREEN.

* test if specified layout exist
  IF NOT P_VARI IS INITIAL.
    CLEAR DEF_LAYOUT.
    MOVE P_VARI  TO DEF_LAYOUT-VARIANT.
    MOVE G_REPID TO DEF_LAYOUT-REPORT.

    CALL FUNCTION 'LVC_VARIANT_EXISTENCE_CHECK'
      EXPORTING
        I_SAVE        = X_SAVE
      CHANGING
        CS_VARIANT    = DEF_LAYOUT
      EXCEPTIONS
        WRONG_INPUT   = 1
        NOT_FOUND     = 2
        PROGRAM_ERROR = 3
        OTHERS        = 4.
    IF SY-SUBRC <> 0.
      MESSAGE ID SY-MSGID TYPE SY-MSGTY NUMBER SY-MSGNO
              WITH SY-MSGV1 SY-MSGV2 SY-MSGV3 SY-MSGV4.
    ENDIF.
  ENDIF.


*----------------------------------------------------------------------*
* START-OF-SELECTION :
*----------------------------------------------------------------------*
START-OF-SELECTION.

** Initialisation des tables, structures et variables
  CLEAR : WGT_AFFICHE, WGT_AFFICHE[],
         WGT_LFB1, WGT_LFB1[], WGT_LFM1, WGT_LFM1[].

* Chercher fournisseurs autorisés :
*  SELECT LIFNR KTOKK INTO TABLE WGT_LFA1 FROM LFA1
*  WHERE KTOKK IN S_KTOKK_TMP.
*  IF SY-SUBRC <> 0.
*    MESSAGE I000(Z_INTERFACES) WITH TEXT-020.
*    STOP.
*  ELSE.
*    SORT WGT_LFA1 BY LIFNR.
*  ENDIF.

** Chercher documents :
  PERFORM R10_EXTRACT_DATA.


*----------------------------------------------------------------------*
* END-OF-SELECTION :
*----------------------------------------------------------------------*
END-OF-SELECTION.

** set gs_variant according to the selection made

  CLEAR GS_VARIANT.
  GS_VARIANT-REPORT = G_REPID.

  IF NOT P_VARI IS INITIAL.
    MOVE-CORRESPONDING DEF_LAYOUT TO GS_VARIANT.
  ENDIF.

  CALL SCREEN 100.

*---------------------------------------------------------------------*
*       MODULE PBO OUTPUT                                             *
*---------------------------------------------------------------------*
MODULE PBO OUTPUT.

  SET PF-STATUS 'MAIN100'.
  SET TITLEBAR '100'.

  IF CUSTOM_CONTAINER IS INITIAL.
* create a custom container control for our ALV Control
    CREATE OBJECT CUSTOM_CONTAINER
      EXPORTING
        CONTAINER_NAME              = MYCONTAINER
      EXCEPTIONS
        CNTL_ERROR                  = 1
        CNTL_SYSTEM_ERROR           = 2
        CREATE_ERROR                = 3
        LIFETIME_ERROR              = 4
        LIFETIME_DYNPRO_DYNPRO_LINK = 5.
    IF SY-SUBRC NE 0.

* add your handling, for example
      CALL FUNCTION 'POPUP_TO_INFORM'
        EXPORTING
          TITEL = G_REPID
          TXT2  = SY-SUBRC
          TXT1  = 'The control could not be created'(510).
    ENDIF.

    CREATE OBJECT GRID1
      EXPORTING
        I_PARENT = CUSTOM_CONTAINER.

    PERFORM R10_FIELDCAT_INIT CHANGING WGT_FIELDCAT[].


    CALL METHOD GRID1->SET_TABLE_FOR_FIRST_DISPLAY
         EXPORTING I_STRUCTURE_NAME = 'ZLISTE_250'
                   IS_VARIANT       = GS_VARIANT
                   I_SAVE           = X_SAVE
                   I_DEFAULT        = P_DEF
*                   is_layout        = ws_layout
         CHANGING  IT_FIELDCATALOG  = WGT_FIELDCAT
                   IT_OUTTAB        = WGT_AFFICHE[].

    PERFORM R10_FIELDCAT_INIT CHANGING WGT_FIELDCAT[].

* Interception des événements d'édition
    CREATE OBJECT EVENT_RECEIVER.
    SET HANDLER EVENT_RECEIVER->HANDLE_TOP_OF_LIST FOR GRID1.
*    SET HANDLER EVENT_RECEIVER->HANDLE_TOP_OF_PAGE FOR GRID1.
*    SET HANDLER EVENT_RECEIVER->HANDLE_END_OF_LIST FOR GRID1.
    SET HANDLER EVENT_RECEIVER->HANDLE_END_OF_PAGE FOR GRID1.
  ENDIF.

ENDMODULE.                    "pbo OUTPUT
*---------------------------------------------------------------------*
*       MODULE PAI INPUT                                              *
*---------------------------------------------------------------------*
MODULE PAI INPUT.

  CASE OK_CODE.
    WHEN 'EXIT'.
      PERFORM EXIT_PROGRAM.
  ENDCASE.

  CLEAR OK_CODE.

ENDMODULE.                    "pai INPUT
*---------------------------------------------------------------------*
*       FORM EXIT_PROGRAM                                             *
*---------------------------------------------------------------------*
FORM EXIT_PROGRAM.

  IF NOT GRID1 IS INITIAL.
    CALL METHOD GRID1->FREE
      EXCEPTIONS
        CNTL_ERROR        = 1
        CNTL_SYSTEM_ERROR = 2
        OTHERS            = 3.
    CLEAR GRID1.
  ENDIF.

  CALL METHOD CUSTOM_CONTAINER->FREE.

  LEAVE TO SCREEN 0.

ENDFORM.                    "exit_program

*&---------------------------------------------------------------------*
*&      Form  r00_init_zones
*&---------------------------------------------------------------------*
*       Zones à afficher sans modification
*----------------------------------------------------------------------*
FORM R00_INIT_ZONES.

  G_REPID = SY-REPID. " Nom du programme en cours
  X_SAVE = 'A'.       " Sauvegarder tout type de mise en page

ENDFORM.                    "r00_init_zones

*&---------------------------------------------------------------------*
*&      Form  r10_extract_data
*&---------------------------------------------------------------------*
FORM R10_EXTRACT_DATA.
  DATA : BEGIN OF WGT_EKKO OCCURS 0,
           EBELN LIKE EKKO-EBELN,
           BUKRS LIKE EKKO-BUKRS,
           BSTYP LIKE EKKO-BSTYP,
           BSART LIKE EKKO-BSART,
           ERNAM LIKE EKKO-ERNAM,
           LIFNR LIKE EKKO-LIFNR,
           NAME1 LIKE LFA1-LIFNR,
           ZTERM LIKE EKKO-ZTERM,
           ZTERM1 LIKE EKKO-ZTERM,
           VTEXT1 LIKE TVZBT-VTEXT,
           ZTERM2 LIKE EKKO-ZTERM,
           VTEXT2 LIKE TVZBT-VTEXT,
           ZTERM3 LIKE EKKO-ZTERM,
           VTEXT3 LIKE TVZBT-VTEXT,
           EKORG LIKE EKKO-ZTERM,
           BEDAT LIKE EKKO-BEDAT,
         END OF WGT_EKKO.

  CLEAR :  WGT_EKKO, WGT_EKKO[].

  SELECT BUKRS
         EBELN
         BSTYP
         BSART
         ERNAM
         LIFNR
         ZTERM
         BEDAT
         EKORG
         FROM EKKO
         INTO CORRESPONDING FIELDS OF TABLE WGT_EKKO
         WHERE
           BEDAT IN S_BEDAT
          AND BSTYP IN S_BSTYP
          AND BSART IN S_BSART
          AND EKGRP IN S_EKGRP
          AND EKORG IN S_EKORG.

  IF WGT_EKKO[] IS INITIAL.
*    MESSAGE E000 WITH TEXT-024.
*    exit.
  ENDIF.

  SORT WGT_EKKO BY LIFNR ZTERM.

* Recherche des cond de paiement dans LFB1/LFM1
  LOOP AT WGT_EKKO.
    WGT_EKKO-ZTERM1 = WGT_EKKO-ZTERM.
    SELECT SINGLE NAME1 FROM LFA1 INTO WGT_EKKO-NAME1 WHERE
                  LIFNR = WGT_EKKO-LIFNR.
    SELECT SINGLE VTEXT FROM TVZBT INTO WGT_EKKO-VTEXT1
           WHERE SPRAS = 'F' AND ZTERM = WGT_EKKO-ZTERM1.
    SELECT SINGLE ZTERM FROM LFB1 INTO  WGT_EKKO-ZTERM2
           WHERE LIFNR = WGT_EKKO-LIFNR AND
                 BUKRS = WGT_EKKO-BUKRS.
    IF SY-SUBRC = 0.
      SELECT SINGLE VTEXT FROM TVZBT INTO WGT_EKKO-VTEXT2
             WHERE SPRAS = 'F' AND ZTERM = WGT_EKKO-ZTERM2.
    ENDIF.
    SELECT SINGLE ZTERM FROM LFM1 INTO  WGT_EKKO-ZTERM3
           WHERE LIFNR = WGT_EKKO-LIFNR AND
                 EKORG = WGT_EKKO-EKORG.
    IF SY-SUBRC = 0.
      SELECT SINGLE VTEXT FROM TVZBT INTO WGT_EKKO-VTEXT3
             WHERE SPRAS = 'F' AND ZTERM = WGT_EKKO-ZTERM3.
    ENDIF.
    MODIFY WGT_EKKO.
  ENDLOOP.
*
  PERFORM MESS USING 'START' TEXT-029.

  LOOP AT WGT_EKKO.
    IF NOT ( WGT_EKKO-ZTERM1 = WGT_EKKO-ZTERM2 AND WGT_EKKO-ZTERM2 = WGT_EKKO-ZTERM3
             AND WGT_EKKO-ZTERM1 = WGT_EKKO-ZTERM3 ).
      MOVE-CORRESPONDING WGT_EKKO TO WGS_AFFICHE.
      MOVE WGT_EKKO-NAME1 TO WGS_AFFICHE-ZNAME1.
      APPEND WGS_AFFICHE TO WGT_AFFICHE.
    ELSE.
      IF ( WGT_EKKO-ZTERM1 = SPACE AND WGT_EKKO-ZTERM2 = SPACE AND WGT_EKKO-ZTERM1 = SPACE ).
        MOVE-CORRESPONDING WGT_EKKO TO WGS_AFFICHE.
        APPEND WGS_AFFICHE TO WGT_AFFICHE.
      ENDIF.
    ENDIF.
  ENDLOOP.

  IF WGT_AFFICHE[] IS INITIAL.
*    MESSAGE E000 WITH TEXT-024.
*
*    STOP.
  ENDIF.

  PERFORM MESS USING 'END' TEXT-029.

ENDFORM.                    " r10_extract_data

*&---------------------------------------------------------------------*
*&      Form  r10_fieldcat_init
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
FORM R10_FIELDCAT_INIT CHANGING PT_FIELDCAT LIKE WGT_FIELDCAT[].

  DATA: LS_FIELDCAT TYPE LVC_S_FCAT.

  CALL FUNCTION 'LVC_FIELDCATALOG_MERGE'
    EXPORTING
      I_STRUCTURE_NAME = 'ZLISTE_250'
    CHANGING
      CT_FIELDCAT      = PT_FIELDCAT.

  LOOP AT PT_FIELDCAT INTO LS_FIELDCAT.
    LS_FIELDCAT-NO_OUT   =  SPACE.

    CASE LS_FIELDCAT-FIELDNAME.
* Nom du FRN
      WHEN 'NAME1'.
        LS_FIELDCAT-SCRTEXT_L = TEXT-018.
        LS_FIELDCAT-SCRTEXT_M = TEXT-018.
        LS_FIELDCAT-SCRTEXT_S = TEXT-018.

* Conditions de paiement
      WHEN 'ZTERM1'.
        LS_FIELDCAT-SCRTEXT_L = TEXT-008.
        LS_FIELDCAT-SCRTEXT_M = TEXT-008.
        LS_FIELDCAT-SCRTEXT_S = TEXT-008.
      WHEN 'ZTERM2'.
        LS_FIELDCAT-SCRTEXT_L = TEXT-009.
        LS_FIELDCAT-SCRTEXT_M = TEXT-009.
        LS_FIELDCAT-SCRTEXT_S = TEXT-009.
      WHEN 'ZTERM3'.
        LS_FIELDCAT-SCRTEXT_L = TEXT-002.
        LS_FIELDCAT-SCRTEXT_M = TEXT-002.
        LS_FIELDCAT-SCRTEXT_S = TEXT-002.
*Groupe d'acheteurs
      WHEN 'EKGRP'.
        LS_FIELDCAT-SCRTEXT_L = TEXT-011.
        LS_FIELDCAT-SCRTEXT_M = TEXT-011.
        LS_FIELDCAT-SCRTEXT_S = TEXT-022.
* Organisation d'achat
      WHEN 'EKORG'.
        LS_FIELDCAT-SCRTEXT_L = TEXT-012.
        LS_FIELDCAT-SCRTEXT_M = TEXT-012.
        LS_FIELDCAT-SCRTEXT_S = TEXT-012.

    ENDCASE.

    MODIFY PT_FIELDCAT FROM LS_FIELDCAT.
  ENDLOOP.

ENDFORM.                    " r10_fieldcat_init

*&---------------------------------------------------------------------*
*&      Form  mess
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
FORM MESS USING P_STEP P_TXT.

  DATA : WL_TXT(80) TYPE C.

  IF SY-BATCH = 'X'.
    MESSAGE S000 WITH P_STEP P_TXT.
    COMMIT WORK.
  ELSE.
    CONCATENATE P_STEP P_TXT INTO WL_TXT SEPARATED BY SPACE.
    CALL FUNCTION 'SAPGUI_PROGRESS_INDICATOR'
         EXPORTING
*              percentage = wgl_perc
              TEXT       = WL_TXT.
  ENDIF.

ENDFORM.                    " mess

