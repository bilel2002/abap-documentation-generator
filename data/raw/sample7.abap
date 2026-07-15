REPORT z_test_03.

START-OF-SELECTION.

PERFORM main.

FORM main.

PERFORM step_one
.
PERFORM step_two .

ENDFORM.

FORM step_one.
SELECT * FROM vbap INTO TABLE @DATA(lt_vbap).
ENDFORM.

FORM step_two.
PERFORM step_three.
ENDFORM.

FORM step_three.
WRITE: / 'STEP 3'.
ENDFORM.