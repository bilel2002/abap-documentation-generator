import re


ABAP_KEYWORDS = {
    "FORM", "ENDFORM",
    "PERFORM",
    "CALL", "FUNCTION",
    "SELECT", "FROM", "WHERE", "JOIN",
    "TABLES",
    "DATA",
    "IF", "ELSE", "ENDIF",
    "LOOP", "ENDLOOP",
    "WRITE",
    "REPORT",
    "INCLUDE",
    "CLASS", "METHOD", "ENDMETHOD",
    "START-OF-SELECTION"
}


def clean_text(raw_text: str) -> str:
    """
    Clean extracted ABAP/text:
    - fixes hyphen cuts
    - merges broken ABAP lines
    - removes only long * comment blocks (>15 consecutive lines)
    - removes inline " comments
    - normalizes spaces
    """

    if not raw_text:
        return ""

    # Fix hyphen-cut words: ENDF-\nORM -> ENDFORM
    raw_text = re.sub(r"-\n", "", raw_text)
    

    # Normalize line endings
    raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    lines = raw_text.split("\n")
    filtered_lines = []

    i = 0
    n = len(lines)

    # --------------------------------------------------
    # Step 1: remove only long * comment blocks (>15 lines)
    #         and remove inline " comments
    # --------------------------------------------------
    while i < n:
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        # Detect a consecutive * comment block
        if line.strip().startswith("*"):
            block = []
            j = i

            while j < n and lines[j].strip().startswith("*"):
                block.append(lines[j])
                j += 1

            # Remove only if block length > 15
            if len(block) <= 15:
                filtered_lines.extend(block)

            i = j
            continue

        # Remove inline " comments
        if '"' in line:
            # Preserve leading whitespace, then remove inline comment
            leading_whitespace = line[:len(line) - len(line.lstrip())]
            stripped_line = line.split('"', 1)[0].rstrip()
            if stripped_line:
                filtered_lines.append(leading_whitespace + stripped_line)
        else:
            filtered_lines.append(line)

        i += 1

    # --------------------------------------------------
    # Step 2: merge ABAP statements
    # --------------------------------------------------
    cleaned_lines = []
    buffer = ""

    for line in filtered_lines:
        stripped_line = line.strip()

        # Skip * comments - add them directly to output
        if stripped_line.startswith("*"):
            if buffer:
                cleaned_lines.append(re.sub(r"[ \t]+", " ", buffer.strip()))
                buffer = ""
            cleaned_lines.append(line)
            continue

        if not stripped_line:
            continue

        first_word = stripped_line.split()[0].upper() if stripped_line.split() else ""

        if first_word in ABAP_KEYWORDS:
            # New ABAP statement starts: flush previous buffer
            if buffer:
                cleaned_lines.append(re.sub(r"[ \t]+", " ", buffer.strip()))
            buffer = stripped_line
        else:
            # Continuation line
            if buffer:
                buffer += " " + stripped_line
            else:
                buffer = stripped_line

        # Flush completed ABAP statements ending with "."
        if stripped_line.endswith("."):
            cleaned_lines.append(re.sub(r"[ \t]+", " ", buffer.strip()))
            buffer = ""

    # Flush remaining buffer
    if buffer:
        cleaned_lines.append(re.sub(r"[ \t]+", " ", buffer.strip()))

    return "\n".join(cleaned_lines)