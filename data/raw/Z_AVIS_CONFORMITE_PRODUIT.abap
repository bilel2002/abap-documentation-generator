************************************************************************
*    Nom du programme : Z_AVIS_CONFORMITE_PRODUIT                      *
*    Auteur           : Eric Berardo - Meltem Consulting               *
*    Date de création : 05.10.2011                                     *
************************************************************************
* Description : Correspondance dans la commande permettant:
* - la création d’un avis qualité de type Z4 (Conformité Produit);
* - l'envoi d'un mail au fournisseur, copie aux achats
************************************************************************
* OT         * Date    * TRI *  Description                            *
************************************************************************
*            *         *     *                                         *
************************************************************************
PROGRAM  z_avis_conformite_produit.

* Déclarations de données
INCLUDE z_avis_conformite_produit_top.

* Routines

*&---------------------------------------------------------------------*
*&      Form  entry
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*      -->ENT_RETCO  text
*      -->ENT_SCREEN text
*----------------------------------------------------------------------*
FORM entry USING ent_retco ent_screen.

* Ne fonctionne qu'en sortie réelle
  CHECK ent_screen IS INITIAL.
  CLEAR ent_retco.

* Sélection des données de commande fournisseur
  PERFORM f_sel_cde USING ent_retco.

* Sélection de l'adresse mail de destination
  PERFORM f_sel_mailto USING ent_retco.

* Sélection des avis déjà existants
  PERFORM f_sel_avis USING ent_retco.

* Création des avis QM
  PERFORM f_creer_avis USING ent_retco.

* Création du mail au fournisseur + copie aux achats
  PERFORM f_mail_fourni USING ent_retco.

ENDFORM.                    "entry

*&---------------------------------------------------------------------*
*&      Form  F_SEL_CDE
*&---------------------------------------------------------------------*
*       Sélection des données de commande fournisseur
*----------------------------------------------------------------------*
FORM f_sel_cde USING ent_retco.

  DATA:
    wlv_kalsk LIKE lfm1-kalsk,
    wlv_atnam LIKE cabn-atnam,
    wlv_atinn LIKE cabn-atinn.

  CLEAR: wgs_ekko, wgv_ekotx.
  REFRESH: wgt_ekpo, wgt_cawnt.

* Sélection des données d'entête
  SELECT SINGLE ebeln bukrs ernam lifnr ekorg ekgrp adrnr
     FROM ekko INTO wgs_ekko
    WHERE ebeln = nast-objky(10).
  IF sy-subrc <> 0.
    ent_retco = 9.
    RETURN.
  ENDIF.

* Sélection des données de poste
  SELECT ebeln ebelp loekz txz01 matnr werks attyp
    FROM ekpo INTO TABLE wgt_ekpo
    WHERE ebeln = nast-objky(10).

* Sélection des données fournisseur
  SELECT SINGLE kalsk
    FROM lfm1 INTO wlv_kalsk
    WHERE lifnr = wgs_ekko-lifnr
    AND ekorg = wgs_ekko-ekorg.
*  IF wlv_kalsk = 'Z4'.
*    IF 1 = 2.
**     Pour que le cas d'emploi fonctionne
*      MESSAGE e013(zqm) WITH wgs_ekko-lifnr wgs_ekko-ekorg wlv_kalsk space.
*    ENDIF.
*    PERFORM protocol_update USING 'ZQM' 013 'E'
*      wgs_ekko-lifnr wgs_ekko-ekorg wlv_kalsk space.
*    ent_retco = 1.
*  ENDIF.

* Détermination de la caractéristique de coloris
  CONCATENATE 'COL_' wgs_ekko-ekorg
  INTO wlv_atnam.
  CALL FUNCTION 'CONVERSION_EXIT_ATINN_INPUT'
    EXPORTING
      input  = wlv_atnam
    IMPORTING
      output = wlv_atinn.
* Sélection des désignations des coloris
  SELECT atwrt atwtb
    FROM cawn JOIN cawnt
    ON cawn~atinn = cawnt~atinn AND cawn~atzhl = cawnt~atzhl
    INTO TABLE wgt_cawnt
    WHERE cawn~atinn = wlv_atinn
    AND cawnt~spras = nast-spras.

* Sélection de la désignation de l'organisation d'achat
  SELECT SINGLE ekotx
    FROM t024e INTO wgv_ekotx
    WHERE ekorg = wgs_ekko-ekorg.

ENDFORM.                    " F_SEL_CDE

*&---------------------------------------------------------------------*
*&      Form  PROTOCOL_UPDATE
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
FORM protocol_update USING  pru_msgid pru_msgno pru_msgty
                            pru_msgv1 pru_msgv2 pru_msgv3 pru_msgv4.

  syst-msgid = pru_msgid.
  syst-msgno = pru_msgno.
  syst-msgty = pru_msgty.
  syst-msgv1 = pru_msgv1.
  syst-msgv2 = pru_msgv2.
  syst-msgv3 = pru_msgv3.
  syst-msgv4 = pru_msgv4.
  CALL FUNCTION 'NAST_PROTOCOL_UPDATE'
    EXPORTING
      msg_arbgb = syst-msgid
      msg_nr    = syst-msgno
      msg_ty    = syst-msgty
      msg_v1    = syst-msgv1
      msg_v2    = syst-msgv2
      msg_v3    = syst-msgv3
      msg_v4    = syst-msgv4
    EXCEPTIONS
      OTHERS    = 1.

ENDFORM.                               " PROTOCOL_UPDATE

*&---------------------------------------------------------------------*
*&      Form  F_CREER_AVIS
*&---------------------------------------------------------------------*
*       Créer avis QM
*----------------------------------------------------------------------*
FORM f_creer_avis  USING  ent_retco.

  DATA:
    wlv_mc LIKE ekpo-matnr, "Modèle-Coloris
    wlv_modele(13) TYPE c,
    wls_notifheader TYPE  bapi2078_nothdri,
    wls_notifheader_export TYPE bapi2078_nothdre,
    wlt_actv TYPE	bapi2078_notactvi OCCURS 0 WITH HEADER LINE,
    wlt_actv2 TYPE  bapi2078_notactvi OCCURS 0 WITH HEADER LINE,
    wlt_return TYPE bapiret2 OCCURS 0 WITH HEADER LINE,
    wlt_notif LIKE TABLE OF wls_notifheader_export-notif_no WITH HEADER LINE.

  CHECK ent_retco IS INITIAL.
  REFRESH wgt_color.

* Remplissage de l'activité (la même pour tous les avis)
  wlt_actv-act_codegrp = wgc_mfgrp. "'ZCERTIF'.
  wlt_actv-act_code = wgc_mfcod.                            "'RCH1'.
  wlt_actv-start_date = sy-datum.
  wlt_actv-act_sort_no = 1.
  wlt_actv-item_sort_no = 1.
  APPEND wlt_actv.

  LOOP AT wgt_ekpo
  WHERE loekz IS INITIAL
  AND attyp = '02'. "On ne s'intéresse qu'aux variantes
    CHECK ent_retco IS INITIAL.

*   On crée un avis par modèle-coloris
    IF wgt_ekpo-matnr(15) <> wlv_mc.
      wlv_mc = wgt_ekpo-matnr(15).

*     Stockage de l'article pour le mail à venir
      CLEAR wgt_color.
      wgt_color-matnr = wgt_ekpo-matnr.
      APPEND wgt_color.

*     On regarde si l'avis existe déjà
      READ TABLE wgt_qmel
        WITH KEY matnr(15) = wlv_mc.
      IF sy-subrc = 0.
*       Avis existant: message dans le log
        CLEAR wlv_modele.
        CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT'
          EXPORTING
            input  = wlv_mc(13)
          IMPORTING
            output = wlv_modele.
        IF 1 = 2.
*         Pour que le cas d'emploi fonctionne
          MESSAGE i012(zqm) WITH wgt_qmel-qmnum wlv_modele wlv_mc+13(2) space.
        ENDIF.
        PERFORM protocol_update USING 'ZQM' 012 'I'
              wgt_qmel-qmnum wlv_modele wlv_mc+13(2) space.

*       On récupère la dernière activité
        CLEAR wgt_qmma.
        READ TABLE wgt_qmma
          WITH KEY qmnum = wgt_qmel-qmnum
          BINARY SEARCH.

*       Remplissage de la nouvelle activité "Relance"
        REFRESH wlt_actv2. CLEAR wlt_actv2.
        wlt_actv2-act_key = wgt_qmma-manum + 1.
        wlt_actv2-act_codegrp = wgc_mfgrp. "'ZCERTIF'.
        wlt_actv2-act_code = wgc_mfcod2.                    "'RCH2'.
        wlt_actv2-start_date = sy-datum.
        wlt_actv2-act_sort_no = wgt_qmma-qmanum + 1.
        wlt_actv2-item_sort_no = wgt_qmma-qmanum + 1.
        APPEND wlt_actv2.

        CLEAR: wls_notifheader_export.
        REFRESH wlt_return.
*       Avis existant: on insère une activité "Relance"
        CALL FUNCTION 'BAPI_QUALNOT_ADD_DATA'
          EXPORTING
            number             = wgt_qmel-qmnum
          IMPORTING
            notifheader_export = wls_notifheader_export
          TABLES
            notifactv          = wlt_actv2
            return             = wlt_return[].

      ELSE.

*       Nouvel avis pour ce modèle-coloris

        CLEAR: wls_notifheader, wls_notifheader_export.
        REFRESH wlt_return.

*       Remplissage des données d'entête
        WRITE wgt_ekpo-ebeln TO wls_notifheader-short_text LEFT-JUSTIFIED.
        wls_notifheader-po_number = wgt_ekpo-ebeln.
        wls_notifheader-po_item = wgt_ekpo-ebelp.
        wls_notifheader-material_plant = wgt_ekpo-werks.
        wls_notifheader-material = wgt_ekpo-matnr.
        wls_notifheader-purch_org = wgs_ekko-ekorg.
        wls_notifheader-pur_group = wgs_ekko-ekgrp.
        wls_notifheader-vend_no = wgs_ekko-lifnr.

*       Création de l'avis
        CALL FUNCTION 'BAPI_QUALNOT_CREATE'
          EXPORTING
            notif_type         = wgc_qmart                  "'Z4'
            notifheader        = wls_notifheader
          IMPORTING
            notifheader_export = wls_notifheader_export
          TABLES
            notifactv          = wlt_actv[]
            return             = wlt_return[].
      ENDIF.

*     Traitement des messages de retour
      LOOP AT wlt_return.
        IF wlt_return-type = 'E'
        OR wlt_return-type = 'A'
        OR wlt_return-type = 'X'.
          ent_retco = 1.
        ENDIF.
        PERFORM protocol_update USING wlt_return-id wlt_return-number
              wlt_return-type wlt_return-message_v1
              wlt_return-message_v2 wlt_return-message_v3 wlt_return-message_v4.
      ENDLOOP.

      CHECK ent_retco IS INITIAL.

*     Sauvegarde de l'avis (qu'il soit créé ou modifié)
      REFRESH wlt_return.
      CALL FUNCTION 'BAPI_QUALNOT_SAVE'
        EXPORTING
          number      = wls_notifheader_export-notif_no
        IMPORTING
          notifheader = wls_notifheader_export
        TABLES
          return      = wlt_return.
      LOOP AT wlt_return.
        IF wlt_return-type = 'E'
        OR wlt_return-type = 'A'
        OR wlt_return-type = 'X'.
          ent_retco = 1.
        ENDIF.
        PERFORM protocol_update USING wlt_return-id wlt_return-number
              wlt_return-type wlt_return-message_v1
              wlt_return-message_v2 wlt_return-message_v3 wlt_return-message_v4.
      ENDLOOP.
      IF ent_retco IS INITIAL.
        APPEND wls_notifheader_export-notif_no TO wlt_notif.

      ENDIF.
    ENDIF.
  ENDLOOP.

  IF ent_retco IS INITIAL.
    LOOP AT wlt_notif.
      PERFORM protocol_update USING 'IM' 405 'S'
            wlt_notif space space space.
    ENDLOOP.
  ENDIF.
ENDFORM.                    " F_CREER_AVIS


*&---------------------------------------------------------------------*
*&      Form  F_SEL_MAILTO
*&---------------------------------------------------------------------*
*       Sélection de l'adresse mail de destination
*----------------------------------------------------------------------*
FORM f_sel_mailto  USING    ent_retco.

  DATA:
    wlv_simu_mail TYPE flag,
    wlv_mail TYPE adr6-smtp_addr,
    wlv_adrnr TYPE lfa1-adrnr,
    BEGIN OF wlt_adr6 OCCURS 0,
      smtp_addr TYPE adr6-smtp_addr,
    END OF wlt_adr6.

  REFRESH wgt_rec.
  CHECK ent_retco IS INITIAL.

  IMPORT wlv_simu_mail FROM MEMORY ID 'ZPARI'.

  IF NOT wlv_simu_mail IS INITIAL.
    CALL FUNCTION 'Z_PARI_UNAME_GET_MAIL'
      EXPORTING
        wiv_uname = sy-uname
      IMPORTING
        wev_mail  = wlv_mail.
    CLEAR wgt_rec.
    wgt_rec-receiver = wlv_mail.
    wgt_rec-rec_type = 'U'.
    APPEND wgt_rec.
  ELSE.
*   Adresse
    IF wgs_ekko-adrnr IS INITIAL.
      SELECT SINGLE adrnr
        FROM lfa1 INTO wlv_adrnr
        WHERE lifnr = wgs_ekko-lifnr.
    ELSE.
      wlv_adrnr = wgs_ekko-adrnr.
    ENDIF.
*   Données mail
    SELECT smtp_addr
      FROM adr6 INTO TABLE wlt_adr6
      WHERE addrnumber = wlv_adrnr
      AND ( flgdefault = 'X' OR flg_nouse = 'X' ).
    IF sy-subrc <> 0.
      SELECT smtp_addr
      FROM adr6 INTO TABLE wlt_adr6
      WHERE addrnumber = wlv_adrnr.
    ENDIF.
*   Remplissage de la table des destinataires mail
    LOOP AT wlt_adr6.
      CLEAR wgt_rec.
      wgt_rec-receiver = wlt_adr6-smtp_addr.
      wgt_rec-rec_type = 'U'.
      APPEND wgt_rec.
    ENDLOOP.
  ENDIF.

* DEB INS ABAP-2448 MSA

*---------------------------------------------------------------------*
* Ajout liste de diffusion UPAP
*---------------------------------------------------------------------*
DATA: wls_rec LIKE wgt_rec.

IF wgs_ekko-ekorg = 'UPAP'.

  CLEAR wls_rec.
  wls_rec-receiver = 'Z_UPAP_REACH'. " Nom de la liste dans SO23
  wls_rec-rec_type = 'C'.            " distribution list
  APPEND wls_rec TO wgt_rec.

ENDIF.
* END INS ABAP-2448 MSA
ENDFORM.                    " F_SEL_MAILTO

*&---------------------------------------------------------------------*
*&      Form  F_MAIL_FOURNI
*&---------------------------------------------------------------------*
*       Création du mail au fournisseur + copie aux achats
*----------------------------------------------------------------------*
FORM f_mail_fourni  USING    ent_retco.

  DATA:
    wlv_adrnr LIKE t001-adrnr,
    wls_adrc TYPE adrc,
    wlv_from LIKE adr6-smtp_addr,
    wlv_mail LIKE adr6-smtp_addr,
    wlv_mail_str TYPE string,
    wlv_ebeln TYPE ekpo-ebeln,
    wlv_ebeln_str TYPE string,
    wlv_sender LIKE soextreci1-receiver,
    wgs_doc_data LIKE sodocchgi1,
    wls_pack_wa TYPE sopcklsti1,
    wlt_packing_list TYPE TABLE OF sopcklsti1 INITIAL SIZE 1,
    wlt_rec TYPE TABLE OF somlreci1 WITH HEADER LINE,
    wgt_obj_contents TYPE TABLE OF solisti1 WITH HEADER LINE,
    wlt_lines TYPE TABLE OF tline WITH HEADER LINE,
    wlv_name LIKE thead-tdname,
    wlv_tabix LIKE sy-tabix,
    wlv_langu LIKE sy-langu,
    wlv_length TYPE i,
    wlv_offset LIKE sy-fdpos,
    wlv_length1 TYPE i,
    wlv_length2 TYPE i,
    wlv_model(18) TYPE c,
    wlv_model_str TYPE string,
    wlv_maktx TYPE makt-maktx,
    wlv_maktx_str TYPE string,
    wlv_matmdl TYPE mara-satnr,
    wlt_stream TYPE string_table,
    wlv_stream LIKE LINE OF wlt_stream,
    wlv_stream1 LIKE LINE OF wlt_stream,
    wlv_newline(1),                    " hex newline
    wlv_cr_lf(1).                      " hex linefeed
  CONSTANTS:
    wlc_from LIKE soextreci1-receiver VALUE 'ETAM@etam.com'.

  CHECK ent_retco IS INITIAL.
  CHECK NOT wgt_color[] IS INITIAL.

* initialization
  CLASS cl_abap_char_utilities DEFINITION LOAD.
  wlv_newline = cl_abap_char_utilities=>newline.
  wlv_cr_lf   = cl_abap_char_utilities=>cr_lf.

* Sélection de l'adresse de la société
  SELECT SINGLE adrnr
    FROM t001 INTO wlv_adrnr
    WHERE bukrs = wgs_ekko-bukrs.
* Sélection des données d'adresse
  SELECT SINGLE *
    FROM adrc INTO wls_adrc
    WHERE addrnumber = wlv_adrnr.

* Mail du créateur de la commande
  CALL FUNCTION 'Z_PARI_UNAME_GET_MAIL'
    EXPORTING
      wiv_uname = wgs_ekko-ernam
    IMPORTING
      wev_mail  = wlv_mail.
  IF wlv_mail IS INITIAL.
    ent_retco = 1.
    PERFORM protocol_update USING 'ZQM' 015 'E'
            wgs_ekko-ernam space space space.
    RETURN.
  ENDIF.

  CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT'
    EXPORTING
      input  = wgs_ekko-ebeln
    IMPORTING
      output = wlv_ebeln.
  CONDENSE wlv_ebeln NO-GAPS.

*- Contenu du mail
  CONCATENATE 'Z_CFP_MAIL_FOURNI_' wgs_ekko-ekorg INTO wlv_name.

* Lecture du contenu du mail
  CALL FUNCTION 'READ_TEXT'
    EXPORTING
      id                      = 'ST'
      language                = nast-spras
      name                    = wlv_name
      object                  = 'TEXT'
    TABLES
      lines                   = wlt_lines
    EXCEPTIONS
      id                      = 1
      language                = 2
      name                    = 3
      not_found               = 4
      object                  = 5
      reference_check         = 6
      wrong_access_to_archive = 7
      OTHERS                  = 8.
  IF sy-subrc <> 0.
    ent_retco = 1.
    PERFORM protocol_update USING sy-msgid sy-msgno
              sy-msgty sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4.
    RETURN.
  ENDIF.

  CLEAR wgt_color.
  READ TABLE wgt_color INDEX 1.
  CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT'
    EXPORTING
      input  = wgt_color-matnr(13)
    IMPORTING
      output = wlv_model.

  CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
    EXPORTING
      input  = wlv_model
    IMPORTING
      output = wlv_matmdl.

  SELECT SINGLE maktx FROM makt INTO wlv_maktx
    WHERE matnr = wlv_matmdl
      AND spras = nast-spras.


  CALL FUNCTION 'CONVERT_ITF_TO_STREAM_TEXT'
    EXPORTING
      language     = nast-spras
      lf           = 'X'
    IMPORTING
      stream_lines = wlt_stream
    TABLES
      itf_text     = wlt_lines.
*       text_stream        = wgt_obj_contents.

  DESCRIBE FIELD wgt_obj_contents
  LENGTH max_stream_line_width IN CHARACTER MODE.

    wlv_mail_str = wlv_mail.
    wlv_ebeln_str = wlv_ebeln.
    wlv_model_str = wlv_model.
    wlv_maktx_str = wlv_maktx.

* On remplit le corps du mail
  LOOP AT wlt_stream INTO wlv_stream.
    IF sy-tabix > 1.
*     Nouvelle ligne: on ajoute CR/LF
*      PERFORM append_text_to_stream TABLES wgt_obj_contents
*                                    USING wlv_cr_lf 1.
*      PERFORM append_text_to_stream TABLES wgt_obj_contents
*                                    USING wlv_newline 1.
      PERFORM append_stream_line TABLES wgt_obj_contents.
    ENDIF.

*   On remplace les variables
    REPLACE 'W_MAIL'  WITH wlv_mail_str  INTO wlv_stream.
    REPLACE 'W_EKORG' WITH wgv_ekotx     INTO wlv_stream.
    REPLACE 'W_EBELN' WITH wlv_ebeln_str INTO wlv_stream.
    REPLACE 'W_EMATN' WITH wlv_model_str INTO wlv_stream.
    REPLACE 'W_TXZ01' WITH wlv_maktx_str INTO wlv_stream.

    SEARCH wlv_stream FOR 'W_COLORIS'.
    IF sy-subrc <> 0.
*     Cas normal: on insère la ligne
      wlv_length = STRLEN( wlv_stream ).
      PERFORM append_text_to_stream
      TABLES wgt_obj_contents USING  wlv_stream wlv_length.

    ELSE.
*     Cas particulier
      wlv_offset = sy-fdpos.
*     On insère le début de la ligne
      wlv_stream1 = wlv_stream(wlv_offset).
      PERFORM append_text_to_stream
      TABLES wgt_obj_contents USING wlv_stream1 wlv_offset.

*     On insère la liste des coloris
      LOOP AT wgt_color.
*       Nouvelle ligne: on ajoute CR/LF
*        PERFORM append_text_to_stream TABLES wgt_obj_contents
*                                      USING wlv_cr_lf 1.
*        PERFORM append_text_to_stream TABLES wgt_obj_contents
*                                      USING wlv_newline 1.
        PERFORM append_stream_line TABLES wgt_obj_contents.
        CLEAR wgt_cawnt.
        READ TABLE wgt_cawnt
          WITH KEY atwrt = wgt_color-matnr+13(2).
        CLEAR wlv_stream1.
        CONCATENATE '-' wgt_color-matnr+13(2) wgt_cawnt-atwtb
        INTO wlv_stream1 SEPARATED BY space.
        wlv_length = STRLEN( wlv_stream1 ).
        PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream1 wlv_length.

      ENDLOOP.

*     Puis on insère la fin de la ligne
      ADD 9 TO wlv_offset.
      CLEAR wlv_stream1.
      wlv_stream1 = wlv_stream+wlv_offset.
      IF NOT wlv_stream1 IS INITIAL.
*       Nouvelle ligne: on ajoute CR/LF
*        PERFORM append_text_to_stream TABLES wgt_obj_contents
*                                      USING wlv_cr_lf 1.
*        PERFORM append_text_to_stream TABLES wgt_obj_contents
*                                      USING wlv_newline 1.
        PERFORM append_stream_line TABLES wgt_obj_contents.
        wlv_length = STRLEN( wlv_stream1 ).
        PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream1 wlv_length.
      ENDIF.
    ENDIF.
  ENDLOOP.
  PERFORM append_stream_line TABLES wgt_obj_contents.

* Ajout de l'adresse de la société

* Ajout du nom 1
  CLEAR wlv_stream.
  wlv_stream = wls_adrc-name1.
  wlv_length = STRLEN( wlv_stream ).
  PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream wlv_length.
  PERFORM append_stream_line TABLES wgt_obj_contents.

* Ajout du nom 4
  CLEAR wlv_stream.
  wlv_stream = wls_adrc-name4.
  wlv_length = STRLEN( wlv_stream ).
  PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream wlv_length.
  PERFORM append_stream_line TABLES wgt_obj_contents.

* Ajout de la rue
  CLEAR wlv_stream.
  CONCATENATE wls_adrc-house_num1 wls_adrc-street INTO wlv_stream SEPARATED BY space.
  SHIFT wlv_stream LEFT DELETING LEADING space.
  wlv_length = STRLEN( wlv_stream ).
  PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream wlv_length.
  PERFORM append_stream_line TABLES wgt_obj_contents.

* Ajout du code postal + ville
  CLEAR wlv_stream.
  CONCATENATE wls_adrc-post_code1 wls_adrc-city1 INTO wlv_stream SEPARATED BY space.
  SHIFT wlv_stream LEFT DELETING LEADING space.
  wlv_length = STRLEN( wlv_stream ).
  PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream wlv_length.
  PERFORM append_stream_line TABLES wgt_obj_contents.

* Ajout du pays
  CLEAR wlv_stream.
  SELECT SINGLE landx
    FROM t005t INTO wlv_stream
    WHERE land1 = wls_adrc-country
    AND spras = nast-spras.
  wlv_length = STRLEN( wlv_stream ).
  PERFORM append_text_to_stream
        TABLES wgt_obj_contents USING wlv_stream wlv_length.
  PERFORM append_stream_line TABLES wgt_obj_contents.

* Récupération de l'adresse d'origine
  IF wgs_ekko-ekorg = 'ZLIN'.
    CALL FUNCTION 'Z_PARI_UNAME_GET_MAIL'
      EXPORTING
        wiv_uname = sy-uname
      IMPORTING
        wev_mail  = wlv_from.
  ELSE.
    CALL FUNCTION 'Z_PARI_UNAME_GET_MAIL'
      EXPORTING
        wiv_uname = nast-usnam
      IMPORTING
        wev_mail  = wlv_from.
  ENDIF.

*- Titre du mail & Type de document
  wlv_langu = sy-langu.
  SET LANGUAGE nast-spras.
  CONCATENATE text-001 wlv_model wlv_maktx INTO wgs_doc_data-obj_descr
  SEPARATED BY space.
  SET LANGUAGE wlv_langu.

  wgs_doc_data-obj_langu = nast-spras.   " Langue du document
  wgs_doc_data-proc_type  = 'R'.         " Report
  wgs_doc_data-proc_name = sy-repid.


* Package joint
  wls_pack_wa-head_start = 1.
  wls_pack_wa-body_start = 1.
  wls_pack_wa-body_num = LINES( wgt_obj_contents ).
  wls_pack_wa-doc_type = 'RAW'.
  APPEND wls_pack_wa TO wlt_packing_list.

* Envoi du premier mail aux adresses du fournisseur
  wlt_rec[] = wgt_rec[].
  wlv_sender = wlv_from.
  CALL FUNCTION 'SO_DOCUMENT_SEND_API1'
    EXPORTING
      document_data              = wgs_doc_data
      sender_address             = wlv_sender
      sender_address_type        = 'INT'
    TABLES
      packing_list               = wlt_packing_list
      contents_txt               = wgt_obj_contents
      receivers                  = wlt_rec[]
    EXCEPTIONS
      too_many_receivers         = 1
      document_not_sent          = 2
      document_type_not_exist    = 3
      operation_no_authorization = 4
      parameter_error            = 5
      x_error                    = 6
      enqueue_error              = 7
      OTHERS                     = 8.
  IF sy-subrc <> 0.
    ent_retco = 1.
    PERFORM protocol_update USING sy-msgid sy-msgno
              sy-msgty sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4.
  ENDIF.

* Envoi d'un deuxième mail aux achats
  REFRESH wlt_rec.
  wlt_rec-receiver = wlv_from.
  wlt_rec-rec_type = 'U'.
  APPEND wlt_rec.

  CALL FUNCTION 'SO_DOCUMENT_SEND_API1'
    EXPORTING
      document_data              = wgs_doc_data
      sender_address             = wlc_from
      sender_address_type        = 'INT'
    TABLES
      packing_list               = wlt_packing_list
      contents_txt               = wgt_obj_contents
      receivers                  = wlt_rec[]
    EXCEPTIONS
      too_many_receivers         = 1
      document_not_sent          = 2
      document_type_not_exist    = 3
      operation_no_authorization = 4
      parameter_error            = 5
      x_error                    = 6
      enqueue_error              = 7
      OTHERS                     = 8.
  IF sy-subrc <> 0.
    ent_retco = 1.
    PERFORM protocol_update USING sy-msgid sy-msgno
              sy-msgty sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4.
  ENDIF.

ENDFORM.                    " F_MAIL_FOURNI

*&---------------------------------------------------------------------*
*&      Form  F_SEL_AVIS
*&---------------------------------------------------------------------*
*       Sélection des avis CFP déjà existants
*----------------------------------------------------------------------*
FORM f_sel_avis  USING    ent_retco.

  DATA wlt_qmma LIKE TABLE OF wgt_qmma WITH HEADER LINE.

  REFRESH: wgt_qmel, wgt_qmma.

  SELECT qmnum matnr ebeln ebelp
    FROM qmel INTO TABLE wgt_qmel
    WHERE qmart = wgc_qmart
    AND lifnum = wgs_ekko-lifnr
    AND ekorg = wgs_ekko-ekorg
    AND bkgrp = wgs_ekko-ekgrp
    AND ebeln = wgs_ekko-ebeln.
  CHECK sy-subrc = 0.

* Sélection des activités
  SELECT qmnum manum qmanum
    FROM qmma INTO TABLE wlt_qmma
    FOR ALL ENTRIES IN wgt_qmel
    WHERE qmnum = wgt_qmel-qmnum.

  SORT wgt_qmel BY matnr.

* On ne garde qu'une ligne d'activité par avis,
* avec le plus haut numéro d'activité/tri
  SORT wlt_qmma BY qmnum.
  LOOP AT wlt_qmma.
    AT NEW qmnum.
      CLEAR wgt_qmma.
      wgt_qmma-qmnum = wlt_qmma-qmnum.
    ENDAT.
    IF wgt_qmma-manum < wlt_qmma-manum.
      wgt_qmma-manum = wlt_qmma-manum.
    ENDIF.
    IF wgt_qmma-qmanum < wlt_qmma-qmanum.
      wgt_qmma-qmanum = wlt_qmma-qmanum.
    ENDIF.
    AT END OF qmnum.
      APPEND wgt_qmma.
    ENDAT.

  ENDLOOP.

ENDFORM.                    " F_SEL_AVIS

*&---------------------------------------------------------------------*
*&      Form  append_text_to_stream
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*      -->TEXT_STREAM    text
*      -->VALUE(TEXT)    text
*      -->VALUE(LENGTH)  text
*----------------------------------------------------------------------*
FORM append_text_to_stream TABLES text_stream
                           USING  value(text)   TYPE any
                                  value(length) TYPE i.
  DATA: l_clen TYPE i,
        l_len  TYPE i.

* handling of single- and multi-byte characters
  WHILE length > 0.
    l_clen = CHARLEN( text ).
    l_len  = act_stream_line_width + l_clen.
    IF l_len > max_stream_line_width.
      IF l_clen > 1.
        l_len = max_stream_line_width - act_stream_line_width.
        IF l_len > 0.
          text_stream+act_stream_line_width(l_len) = text(l_len).
          SHIFT text BY l_len PLACES.
          length = length - l_len.
          l_clen = l_clen - l_len.
        ENDIF.
      ENDIF.
      PERFORM append_stream_line TABLES text_stream.
    ENDIF.
    text_stream+act_stream_line_width(l_clen) = text(l_clen).
    act_stream_line_width = act_stream_line_width + l_clen.
    SHIFT text BY l_clen PLACES.
    length = length - l_clen.
  ENDWHILE.

ENDFORM.                               "append_text_to_stream

*----------------------------------------------------------------------*
*       FORM  append_stream_line
*----------------------------------------------------------------------*
*       append stream line to stream table
*----------------------------------------------------------------------*
*  -->  text_stream table of text stream (with header line)
*----------------------------------------------------------------------*
FORM append_stream_line TABLES text_stream.

*  if text_stream <> space.
  APPEND text_stream.
  PERFORM clear_stream_line USING text_stream.
*  endif.

ENDFORM.                               "append_stream_line

*----------------------------------------------------------------------*
*       FORM  clear_stream_line
*----------------------------------------------------------------------*
*       initialization of stream table line
*----------------------------------------------------------------------*
*  -->  stream_line line of stream table
*----------------------------------------------------------------------*
FORM clear_stream_line USING stream_line TYPE any.

  CLEAR: stream_line,
         act_stream_line_width.

ENDFORM.                               "clear_stream_line

