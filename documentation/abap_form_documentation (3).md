# ABAP Program Documentation


## FORM: ENTRY

 # Technical Documentation for ABAP Form ENTRY

## Overview

The ABAP form `ENTRY` is an essential component of the application, serving as a central point to execute various functions related to creating and sending notifications to suppliers. This form does not get called by any other PERFORMs.

## Call Information

The `ENTRY` form is not called by any other PERFORMs.

## Function Modules Called

No function modules are called within the `ENTRY` form.

## SAP Tables Accessed

No SAP tables are accessed within the `ENTRY` form.

## Select Statements

No select statements are used within the `ENTRY` form.

## Internal Tables Used

No internal tables are used within the `ENTRY` form.

## Source Code Analysis

The source code for the `ENTRY` form is as follows:

```abap
Form  entry
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*      -->ENT_RETCO  text
*      -->ENT_SCREEN text
*----------------------------------------------------------------------*
FORM entry USING ent_retco ent_screen.
* Ne fonctionne qu'en sortie relle
CHECK ent_screen IS INITIAL.
CLEAR ent_retco.
* Slection des donnes de commande fournisseur
PERFORM f_sel_cde USING ent_retco.
* Slection de l'adresse mail de destination
PERFORM f_sel_mailto USING ent_retco.
* Slection des avis dj existants
PERFORM f_sel_avis USING ent_retco.
* Cration des avis QM
PERFORM f_creer_avis USING ent_retco.
* Cration du mail au fournisseur + copie aux achats
PERFORM f_mail_fourni USING ent_retco.
ENDFORM
```

The `ENTRY` form initializes the internal tables `ENT_RETCO` and `ENT_SCREEN`. It then performs several functions to select command data for suppliers, destination email addresses, existing advisories, creating QM advisories, creating emails to suppliers, and copying the emails to purchases. The form only works in a real output scenario.

## Function Descriptions

1. `f_sel_cde`: Selects the command data for suppliers.
2. `f_sel_mailto`: Selects the destination email addresses.
3. `f_sel_avis`: Selects existing advisories.
4. `f_creer_avis`: Creates QM advisories.
5. `f_mail_fourni`: Creates emails to suppliers and copies them to purchases.

---


## FORM: F_SEL_CDE

 **Title:** Documentation for ABAP Form F_SEL_CDE

**Description:** This document provides a detailed explanation of the ABAP form F_SEL_CDE, which is used for selecting data related to supplier orders.

**Form Name:** F_SEL_CDE

**Call Information:**
- Form: "F_SEL_CDE"
- Call Count: 1
- Called at Positions: []

**Function Modules Called:**
- CONVERSION_EXIT_ATINN_INPUT

**SAP Tables Accessed:**
- EKKO, EKPO, LFM1, CAWN, CAWNT, T024E

**Select Statements:**
- EKKO: Retrieves data related to the order header.
- EKPO: Retrieves data related to the order items.
- LFM1: Retrieves the KALSK field (customer group).
- CAWN: Retrieves the ATWRT and ATWTB fields (color designations).
- T024E: Retrieves the EKOTX field (purchasing organization designation).

**Internal Tables Used:**
None

**Source Code:**
The source code for F_SEL_CDE is provided below. It consists of several sections, each performing a specific task:

1. Initialization and selection of the order header data.
2. Selection of the order item data.
3. Selection of the customer group (KALSK).
4. Determination of the color characteristic (ATNAM) and its conversion using CONVERSION_EXIT_ATINN_INPUT function module.
5. Selection of the color designations (ATWRT and ATWTB).
6. Selection of the purchasing organization designation (EKOTX).

**Notes:**
- The commented code sections (indicated by **) are not currently being used in the form.
- The form includes an IF condition that checks if the customer group is 'Z4'. If this condition is met, it performs some additional operations related to protocol update and setting the return code (ent_retco). However, these operations are currently commented out.

---


## FORM: PROTOCOL_UPDATE

 # Technical Documentation for ABAP Form: PROTOCOL_UPDATE

## Overview

The `PROTOCOL_UPDATE` form is a custom ABAP form designed to interact with the SAP system. This form is called eight times, and it does not call any other forms at specific positions.

## Functionality

The primary function of this form is to update protocol-related data by calling the `NAST_PROTOCOL_UPDATE` function module. The function module takes six parameters: `msg_arbgb`, `msg_nr`, `msg_ty`, `msg_v1`, `msg_v2`, `msg_v3`, and `msg_v4`. These parameters are populated with the values passed to the form, specifically `pru_msgid`, `pru_msgno`, `pru_msgty`, `pru_msgv1`, `pru_msgv2`, `pru_msgv3`, and `pru_msgv4`.

## Data Access

The form does not access any SAP tables or use any internal tables. Instead, it directly manipulates the system-defined variables `syst-msgid`, `syst-msgno`, `syst-msgty`, `syst-msgv1`, `syst-msgv2`, `syst-msgv3`, and `syst-msgv4`.

## Exceptions

The form is designed to handle exceptions that may occur during the execution of the `NAST_PROTOCOL_UPDATE` function module. If any such exception occurs, the form will terminate with an "OTHERS" exception.

## Source Code

Here's the source code for the `PROTOCOL_UPDATE` form:

```abap
Form  PROTOCOL_UPDATE
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
FORM protocol_update USING pru_msgid pru_msgno pru_msgty pru_msgv1 pru_msgv2 pru_msgv3 pru_msgv4.
syst-msgid = pru_msgid.
syst-msgno = pru_msgno.
syst-msgty = pru_msgty.
syst-msgv1 = pru_msgv1.
syst-msgv2 = pru_msgv2.
syst-msgv3 = pru_msgv3.
syst-msgv4 = pru_msgv4.
CALL FUNCTION 'NAST_PROTOCOL_UPDATE' EXPORTING msg_arbgb = syst-msgid msg_nr = syst-msgno msg_ty = syst-msgty msg_v1 = syst-msgv1 msg_v2 = syst-msgv2 msg_v3 = syst-msgv3 msg_v4 = syst-msgv4 EXCEPTIONS OTHERS = 1.
ENDFORM
```

---


## FORM: F_CREER_AVIS

 # Technical Documentation for ABAP Form F_CREER_AVIS

## Overview

Form `F_CREER_AVIS` is designed to create quality management (QM) notifications based on the data from the sales order (EKPO) table. The form calls three function modules and accesses two SAP tables, EKPO and QMEL. It also uses no internal tables.

## Form Details

**Form Name:** F_CREER_AVIS

**Call Information:**
```json
{
  "form": "F_CREER_AVIS",
  "call_count": 1,
  "called_at_positions": []
}
```

## Function Modules Called

1. CONVERSION_EXIT_ALPHA_OUTPUT
2. BAPI_QUALNOT_ADD_DATA
3. BAPI_QUALNOT_SAVE

## SAP Tables Accessed

1. EKPO
2. QMEL

## Select Statements

1. EKPO table with fields: `EBELN`, `EBELP`, `LOEKZ`, `TXZ01`, `MATNR`, `WERKS`, and `ATTYP`
2. QMEL table with fields: `QMNUM`, `MATNR`, `EBELN`, and `EBELP`

## Internal Tables Used

None

## Source Code

The source code for the form is provided below:

```abap
Form  F_CREER_AVIS
*&---------------------------------------------------------------------*
*       Crer avis QM
*----------------------------------------------------------------------*
FORM f_creer_avis USING ent_retco.
DATA: wlv_mc LIKE ekpo-matnr, wlv_modele(13) TYPE c, wls_notifheader TYPE bapi2078_nothdri, wls_notifheader_export TYPE bapi2078_nothdre, wlt_actv TYPE bapi2078_notactvi OCCURS 0 WITH HEADER LINE, wlt_actv2 TYPE bapi2078_notactvi OCCURS 0 WITH HEADER LINE, wlt_return TYPE bapiret2 OCCURS 0 WITH HEADER LINE, wlt_notif LIKE TABLE OF wls_notifheader_export-notif_no WITH HEADER LINE.
CHECK ent_retco IS INITIAL.
REFRESH wgt_color.
* Remplissage de l'activit (la mme pour tous les avis)
wlt_actv-act_codegrp = wgc_mfgrp.
wlt_actv-act_code = wgc_mfcod.
wlt_actv-start_date = sy-datum.
wlt_actv-act_sort_no = 1.
wlt_actv-item_sort_no = 1.
APPEND wlt_actv.
LOOP AT wgt_ekpo
WHERE loekz IS INITIAL AND attyp = '02'.
CHECK ent_retco IS INITIAL.
*   On cre un avis par modle-coloris
IF wgt_ekpo-matnr(15) <> wlv_mc.
wlv_mc = wgt_ekpo-matnr(15).
*     Stockage de l'article pour le mail  venir
CLEAR wgt_color.
wgt_color-matnr = wgt_ekpo-matnr.
APPEND wgt_color.
*     On regarde si l'avis existe dj
READ TABLE wgt_qmel WITH KEY matnr(15) = wlv_mc.
IF sy-subrc = 0.
*       Avis existant: message dans le log
CLEAR wlv_modele.
CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT' EXPORTING input = wlv_mc(13) IMPORTING output = wlv_modele.
IF 1 = 2.
*         Pour que le cas d'emploi fonctionne
MESSAGE i012(zqm) WITH wgt_qmel-qmnum wlv_modele wlv_mc+1

---


## FORM: F_SEL_MAILTO

 **Title:** Technical Documentation for Form F\_SEL\_MAILTO

**Description:** This document provides an overview of the ABAP form F\_SEL\_MAILTO, which is used to select the email destination address.

**Form Name:** F\_SEL\_MAILTO

**Call Information:**
- Form: `F_SEL_MAILTO`
- Call Count: 1
- Called at Positions: []

**Function Modules Called:**
- Z\_PARI\_UNAME\_GET\_MAIL

**SAP Tables Accessed:**
- MEMORY, LFA1, ADR6, EKKO, T001

**Select Statements:**
- EKKO: Retrieves data related to the document header.
- LFA1: Retrieves the address number for a specific life number.
- ADR6: Retrieves the SMTP address based on the address number.
- T001: Not used in this form.

**Internal Tables Used:**
None

**Source Code Overview:**
The F\_SEL\_MAILTO form is designed to select the email destination address. It checks if a simulation mail flag is set, and if so, it retrieves the user's email address using the Z\_PARI\_UNAME\_GET\_MAIL function module. If no simulation mail flag is set, it retrieves the email address from the EKKO and ADR6 tables based on the document header and address number. The form also includes an optional addition of a distribution list for UPAP documents.

**Form Code:**
```abap
Form  F_SEL_MAILTO
...
* Code for selecting and processing email addresses
...
* Addition of UPAP distribution list (optional)
...
ENDFORM
```

**Additional Information:**
- The form includes a check to ensure that the return control data is initialized.
- The form includes a check for errors when accessing the ADR6 table. If an error occurs, it attempts to retrieve the SMTP address again.
- The form includes an optional addition of a distribution list for UPAP documents (Z_UPAP_REACH) when the document type is UPAP.

---


## FORM: F_MAIL_FOURNI

 **Title:** Documentation for ABAP Form F_MAIL_FOURNI

**Description:** This document provides a detailed description of the ABAP form F_MAIL_FOURNI, which is used to create and send emails to suppliers along with packing lists.

**Form Name:** F_MAIL_FOURNI

**Call Information:**
- Form: `F_MAIL_FOURNI`
- Call Count: 1
- Called at Positions: []

**Function Modules Called:**
1. CONVERSION_EXIT_ALPHA_OUTPUT
2. Z_PARI_UNAME_GET_MAIL
3. READ_TEXT
4. CONVERSION_EXIT_ALPHA_INPUT
5. CONVERT_ITF_TO_STREAM_TEXT
6. SO_DOCUMENT_SEND_API1

**SAP Tables Accessed:**
- EKPO
- ADR6
- T001
- ADRC
- MAKT

**Select Statements:**
- [EKKO, EKPO, LFA1, ADR6, T001, ADRC, MAKT, T005T] with various fields and conditions.

**Internal Tables Used:**
None

**Form Purpose:** The purpose of this form is to create an email for a supplier containing the packing list details of a sales order. Additionally, it sends a copy of the email to the purchasing department.

**Source Code Overview:**
The source code initializes necessary variables and constants, performs selections to fetch data from various tables, calls function modules to convert text and send emails, and handles exceptions and error conditions. The main logic involves reading the content of the email, converting product model names, extracting relevant data, and sending the email using the SO_DOCUMENT_SEND_API1 function module.

**Detailed Functionality:**

1. Initialization: Loads the ABAP Char Utilities class for handling character-related operations.
2. Selection of the sender's address: Retrieves the sender's email address based on the sales order data.
3. Fetching the recipient's address: Queries the T001 and ADRC tables to get the recipient's address.
4. Getting the creator's email: Calls the Z_PARI_UNAME_GET_MAIL function module to obtain the email of the sales order creator.
5. Reading the email content: Uses the READ_TEXT function module to read the email content from the system.
6. Converting product model names: Calls CONVERSION_EXIT_ALPHA_OUTPUT and CONVERSION_EXIT_ALPHA_INPUT function modules to convert product model names between alpha and numeric formats.
7. Extracting relevant data: Queries the MAKT table to get the product name in the recipient's language, and converts the ITF text into a stream of strings.
8. Filling the email body: Loops through the stream of strings and appends them to the email content, adding newlines and formatting as necessary.
9. Sending the email: Calls SO_DOCUMENT_SEND_API1 function module to send the email with the packing list attached as a PDF.
10. Sending a copy to purchasing: Sends a second email to the purchasing department with the same content and attachments.

---


## FORM: F_SEL_AVIS

 **Title:** Technical Documentation for ABAP Form F_SEL_AVIS

**Description:** This document provides an overview of the ABAP form `F_SEL_AVIS`, which is used to select existing CFP reviews (avis). The form retrieves data from SAP tables QMEL, QMMA, and EKKO.

**Form Name:** F_SEL_AVIS

**Call Information:**
- Form: "F_SEL_AVIS"
- Call Count: 1
- Called at Positions: []

**Function Modules Called:** None

**SAP Tables Accessed:**
- EKKO (Fields: EBELN, BUKRS, ERNAM, LIFNR, EKORG, EKGRP, ADRNR)
- QMEL (Fields: QMNUM, MATNR, EBELN, EBELP)
- QMMA (Fields: QMNUM, MANUM, QMANUM)

**Select Statements:**
1. SELECT statement for table EKKO to retrieve data related to the document.
2. SELECT statement for table QMEL to fetch quality control inspection data.
3. SELECT statement for table QMMA to get manufacturing order data.

**Internal Tables Used:** None

**Source Code:**
```abap
Form  F_SEL_AVIS
*&---------------------------------------------------------------------*
*       Slection des avis CFP dj existants
*----------------------------------------------------------------------*
FORM f_sel_avis USING ent_retco.
DATA wlt_qmma LIKE TABLE OF wgt_qmma WITH HEADER LINE.
REFRESH: wgt_qmel, wgt_qmma.
SELECT qmnum matnr ebeln ebelp
FROM qmel INTO TABLE wgt_qmel
WHERE qmart = wgc_qmart AND lifnum = wgs_ekko-lifnr AND ekorg = wgs_ekko-ekorg AND bkgrp = wgs_ekko-ekgrp AND ebeln = wgs_ekko-ebeln.
CHECK sy-subrc = 0.
* Slection des activits
SELECT qmnum manum qmanum
FROM qmma INTO TABLE wlt_qmma FOR ALL ENTRIES IN wgt_qmel
WHERE qmnum = wgt_qmel-qmnum.
SORT wgt_qmel BY matnr.
* On ne garde qu'une ligne d'activit par avis,
* avec le plus haut numro d'activit/tri
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
ENDFORM
```

**Functionality:** The form `F_SEL_AVIS` is designed to select existing CFP reviews (avis) by retrieving data from SAP tables EKKO, QMEL, and QMMA. It first fetches quality control inspection data from table QMEL based on certain conditions such as the material number, lifnr, ekorg, bkgrp, and ebeln. Then it gets manufacturing order data from table QMMA for each inspection record found in the previous step. The form sorts both tables by material number (matnr) and merges them to keep only one line of activity per avis with the highest activity number.

**Notes:**
- This documentation is based on the provided source code and may not cover all aspects or potential modifications of the form `F_SEL_AVIS`.
- Always ensure proper testing and validation when implementing or modifying ABAP code in a production environment.

---


## FORM: APPEND_TEXT_TO_STREAM

 # Technical Documentation for ABAP Form: APPEND_TEXT_TO_STREAM

## Overview

The `APPEND_TEXT_TO_STREAM` form is designed to append text to a stream, handling both single- and multi-byte characters. This form does not call any function modules or access SAP tables, select statements, or internal tables.

## Form Details

**Form Name:** APPEND_TEXT_TO_STREAM

**Description:** Appends text to a stream, handling both single- and multi-byte characters.

## Input Parameters

The form accepts the following input parameters:

1. `text_stream` (Table): The target stream where the text will be appended.
2. `value(text)` (Type any): The text to be appended to the stream.
3. `value(length)` (Type i): The length of the input text.

## Internal Variables

1. `l_clen` (Type i): Temporary variable used for character length calculations.
2. `l_len` (Type i): Temporary variable used for line width calculations.
3. `act_stream_line_width`: Represents the current active line width in the stream.

## Functionality

The form processes the input text character by character until the entire length is processed. It handles line wrapping if the line width exceeds the maximum allowed line width (`max_stream_line_width`). The form performs an `append_stream_line` subroutine for each complete line.

## Subroutines

1. `append_stream_line`: This subroutine is responsible for appending a completed line to the stream. It is called when a line has been fully processed or when a line wrap occurs due to exceeding the maximum allowed line width.

## Limitations and Assumptions

- The form assumes that the input text is properly initialized with the correct length.
- The form does not handle special cases such as embedded control characters or non-printable characters.
- The form does not check for buffer overflow in the stream. It is assumed that the stream has sufficient capacity to accommodate the input text.

---


## FORM: APPEND_STREAM_LINE

 # Technical Documentation for ABAP Form APPEND_STREAM_LINE

## Overview

The `APPEND_STREAM_LINE` form is designed to append a line from the `text_stream` table to a stream table, if the `text_stream` table contains data. After appending, the form performs a clear operation on the `text_stream` line using the `clear_stream_line` subroutine.

## Call Information

The `APPEND_STREAM_LINE` form is called 10 times in the system. It does not have any specific positions where it is called, as indicated by the empty `called_at_positions` array.

## Function Modules Called

No function modules are called within this form.

## SAP Tables Accessed

No SAP tables are accessed within this form.

## Select Statements

No select statements are used within this form.

## Internal Tables Used

The only internal table used in this form is the `text_stream` table, which is a table of `text stream (with header line)`.

## Source Code

```abap
FORM  append_stream_line
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
ENDFORM
```

## Detailed Explanation

The `append_stream_line` form begins by defining its input parameter, the `text_stream` table. This table is of type `text stream (with header line)`.

The form then checks if the `text_stream` table contains any data (i.e., it's not empty). If it does contain data, the form appends this data to the stream table using the `APPEND` statement. After appending, the form performs a clear operation on the `text_stream` line using the `clear_stream_line` subroutine and the specified `text_stream` parameter.

If the `text_stream` table is empty, no action is taken within this form.

---


## FORM: CLEAR_STREAM_LINE

 # Technical Documentation for ABAP Form CLEAR_STREAM_LINE

## Overview

The ABAP form `CLEAR_STREAM_LINE` is designed to initialize the line of a stream table. This form does not call any function modules, access SAP tables, or use internal tables. It only uses one parameter, `stream_line`, which is of type `any`.

## Form Details

### Form Name

The name of the form is `CLEAR_STREAM_LINE`.

### Call Information

- The form is called once (`call_count`: 1).
- It is not called at any specific positions within the code (`called_at_positions`: []).

### Function Modules Called

No function modules are called within this form.

### SAP Tables Accessed

No SAP tables are accessed within this form.

### Select Statements

No select statements are used within this form.

### Internal Tables Used

No internal tables are used within this form.

## Source Code

The source code for the `CLEAR_STREAM_LINE` form is as follows:

```abap
FORM  clear_stream_line
*----------------------------------------------------------------------*
*       initialization of stream table line
*----------------------------------------------------------------------*
*  -->  stream_line line of stream table
*----------------------------------------------------------------------*
FORM clear_stream_line USING stream_line TYPE any.
CLEAR: stream_line, act_stream_line_width.
ENDFORM
```

In this code, the form `clear_stream_line` is defined with one parameter, `stream_line`, which is of type `any`. The form initializes two variables: `stream_line` and `act_stream_line_width`. These variables are cleared using the `CLEAR` statement.

---
