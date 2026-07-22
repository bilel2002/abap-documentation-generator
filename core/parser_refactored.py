import re
from typing import List, Tuple


def parse_abap(code: str):
    normalized_code = normalize_for_parser(code)
    method_calls, set_handler_registrations = extract_method_calls_and_handlers(normalized_code)
    return {
        "forms": extract_forms(normalized_code),
        "performs": extract_performs(normalized_code),
        "selects": extract_selects(normalized_code),
        "function_calls": extract_function_calls(normalized_code),
        "sap_tables_used": extract_sap_tables(normalized_code),
        "internal_tables": extract_internal_tables(normalized_code),
        "classes": extract_classes(normalized_code),
        "methods": extract_methods(normalized_code),
        "method_calls": method_calls,
        "set_handler_registrations": set_handler_registrations
    }


# --- Code normalization
def normalize_for_parser(code: str) -> str:
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines = []
    important_keywords = {"METHOD", "METHODS", "CLASS-METHODS", "ENDMETHOD", "ENDCLASS", "CLASS"}
    for line in code.split("\n"):
        stripped = line.strip()
        if stripped.startswith("*"):
            content = stripped.lstrip("*").strip()
            upper_content = content.upper()
            if upper_content.startswith(("CALL METHOD", "SET HANDLER")):
                continue
            has_important = any(keyword in upper_content for keyword in important_keywords)
            if not has_important:
                continue
            line = content
        if '"' in line:
            line = line.split('"', 1)[0]
        if line.strip():
            cleaned_lines.append(line.rstrip())
    return re.sub(r"[ \t]+", " ", "\n".join(cleaned_lines))


# --- Helper: Extract forms/performs/function calls
def extract_forms(code: str):
    forms = re.findall(r"\bFORM\s+([A-Z0-9_]+)\b", code, flags=re.IGNORECASE)
    return unique_preserve_order([f.upper() for f in forms])


def extract_performs(code: str):
    performs = re.findall(r"\bPERFORM\s+([A-Z0-9_]+)\b", code, flags=re.IGNORECASE)
    return [p.upper() for p in performs]


def extract_function_calls(code: str):
    calls = re.findall(r"\bCALL\s+FUNCTION\s+'?([A-Z0-9_]+)'?\b", code, flags=re.IGNORECASE)
    return [c.upper() for c in calls]


# --- Helper: Unique, order preserved deduplication
def unique_preserve_order(items):
    seen = set()
    return [item for item in items if item not in seen and not seen.add(item)]


# --- SAP tables extraction
def extract_sap_tables(code: str):
    code_no_strings = re.sub(r"'[^']*'", "''", code)
    occurrences = []
    patterns = [
        (r"(?ims)^\s*TABLES\s*:\s*(.*?)\.", "tables_decl"),
        (r"\bFROM\s+([A-Z][A-Z0-9_]+)\b", "simple"),
        (r"\bJOIN\s+([A-Z][A-Z0-9_]+)\b", "simple"),
        (r"\bINSERT\s+INTO\s+([A-Z][A-Z0-9_]+)\b", "simple"),
        (r"\bUPDATE\s+([A-Z][A-Z0-9_]+)\b", "simple"),
        (r"\bDELETE\s+FROM\s+([A-Z][A-Z0-9_]+)\b", "simple"),
        (r"\bMODIFY\s+([A-Z][A-Z0-9_]+)\b", "simple"),
    ]

    for pattern, type_ in patterns:
        for match in re.finditer(pattern, code_no_strings, flags=re.IGNORECASE):
            occurrences.append((match.start(), type_, match.group(1)))

    occurrences.sort(key=lambda x: x[0])
    tables = []

    for _, type_, value in occurrences:
        if type_ == "tables_decl":
            block = value.replace("\n", " ")
            for item in [x.strip() for x in block.split(",") if x.strip()]:
                token = item.split()[0].strip().upper()
                if is_probable_db_table(token):
                    tables.append(token)
        else:
            token = value.upper()
            if is_probable_db_table(token):
                tables.append(token)

    return unique_preserve_order(tables)


def is_probable_db_table(token: str):
    if not token:
        return False
    token = token.upper()
    forbidden = {
        "EXCEPTIONS", "OTHERS", "TABLE", "TABLES", "INTO", "FROM", "JOIN", 
        "WHERE", "SET", "VALUES", "DATA", "EXPORTING", "IMPORTING", "CHANGING","MEMORY"
    }
    if token in forbidden:
        return False
    bad_prefixes = (
        "LT_", "GT_", "IT_", "ET_", "RT_", "CT_", "LS_", "GS_", "WA_", "LV_", "GV_", 
        "WGT_", "PT_", "W_", "MT_", "T_", "WT_", "ST_", 
        "ALV_", "GRID_", "CONTAINER_"
    )
    if token.startswith(bad_prefixes):
        return False
    bad_substrings = ("GRID", "CONTAINER", "ALV", "CONTROL")
    if any(sub in token for sub in bad_substrings):
        return False
    return bool(re.match(r"^[A-Z][A-Z0-9_]*$", token))


# --- SELECT statements extraction
def extract_selects(code: str):
    selects = []
    select_blocks = re.findall(r"\bSELECT\b.*?\.", code, flags=re.IGNORECASE | re.DOTALL)
    for block in select_blocks:
        parsed = parse_select_block(block)
        if parsed and (parsed["table"] or parsed["fields"] or parsed["into"]["targets"]):
            selects.append(parsed)
    return selects


def parse_select_block(block: str):
    compact = re.sub(r"\s+", " ", block.strip()).rstrip(".")
    if not re.match(r"^\bSELECT\b", compact, flags=re.IGNORECASE):
        return None
    obj = {"table": None, "fields": [], "into": {"targets": []}}
    from_match = re.search(r"\bFROM\s+([A-Z0-9_]+)\b", compact, flags=re.IGNORECASE)
    if from_match:
        obj["table"] = from_match.group(1).upper()
    obj["fields"] = extract_select_fields(compact)
    obj["into"]["targets"] = extract_into_targets(compact)
    return obj


def extract_select_fields(select_stmt: str):
    m = re.search(r"\bSELECT\b\s+(.*?)\s+\bFROM\b", select_stmt, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    field_part = m.group(1).strip()
    field_part = re.sub(r"^\bSINGLE\b\s*", "", field_part, flags=re.IGNORECASE)
    field_part = re.sub(r"^\bDISTINCT\b\s*", "", field_part, flags=re.IGNORECASE)
    if not field_part:
        return []
    if field_part == "*":
        return ["*"]
    tokens = [t.strip() for t in field_part.replace(",", " ").split() if t.strip()]
    fields = []
    forbidden = {
        "SINGLE", "DISTINCT", "FROM", "INTO", "WHERE", "GROUP", "BY", "ORDER", "HAVING",
        "APPENDING", "TABLE", "UP", "TO", "ROWS", "PACKAGE", "SIZE", "BYPASSING", "BUFFER",
        "CLIENT", "SPECIFIED", "FOR", "ALL", "ENTRIES", "AS"
    }
    for token in tokens:
        token_clean = token.strip().rstrip(",").replace("@", "")
        if not token_clean or token_clean.upper() in forbidden:
            continue
        fields.append(token_clean.upper())
    return unique_preserve_order(fields)


def extract_into_targets(select_stmt: str):
    m = re.search(
        r"\bINTO\b\s+(.*?)(?=\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bHAVING\b|\bUP\s+TO\b|\bPACKAGE\s+SIZE\b|\bBYPASSING\s+BUFFER\b|\bCLIENT\s+SPECIFIED\b|\bFOR\s+ALL\s+ENTRIES\b|$)",
        select_stmt, flags=re.IGNORECASE | re.DOTALL
    )
    if not m:
        return []
    into_part = m.group(1).strip()
    into_part = re.sub(r"\b(TABLE|CORRESPONDING|FIELDS|OF|DATA)\b", " ", into_part, flags=re.IGNORECASE)
    into_part = into_part.replace("@", " ").replace("(", " ").replace(")", " ").replace(",", " ")
    tokens = [t.strip() for t in into_part.split() if t.strip()]
    targets = []
    forbidden = {"INTO", "TABLE", "CORRESPONDING", "FIELDS", "OF", "DATA"}
    bad_prefixes = (
        "LT_", "GT_", "IT_", "ET_", "RT_", "CT_", "LS_", "GS_", "WA_", "LV_", "GV_", 
        "WGT_", "PT_", "W_", "MT_", "T_", "GT_", "L_", "G_", "T_", "WT_", "ST_", 
        "ALV_", "GRID_", "CONTAINER_"
    )
    bad_substrings = ("GRID", "CONTAINER", "ALV", "CONTROL")
    for token in tokens:
        upper = token.upper()
        if upper in forbidden:
            continue
        if upper.startswith(bad_prefixes):
            continue
        if any(sub in upper for sub in bad_substrings):
            continue
        if is_identifier(upper):
            targets.append(upper)
    return unique_preserve_order(targets)


def is_identifier(token: str):
    return bool(re.match(r"^[A-Z_][A-Z0-9_~\-]*$", token, flags=re.IGNORECASE))


# --- Internal tables extraction
def extract_internal_tables(code: str):
    code_no_strings = re.sub(r"'[^']*'", "''", code)
    patterns = [
        r"\bDATA\s+([A-Z][A-Z0-9_]+)\s+(?:TYPE|LIKE)\s+(?:STANDARD\s+|SORTED\s+|HASHED\s+)?TABLE\s+OF",
        r"\bDATA\s*:\s*([A-Z][A-Z0-9_]+)\s+(?:TYPE|LIKE)\s+(?:STANDARD\s+|SORTED\s+|HASHED\s+)?TABLE\s+OF",
        r"\bDATA\s+:\s*([A-Z][A-Z0-9_]+)\s+(?:TYPE)\s+[A-Z][A-Z0-9_~\-]+(?:WITH NON-UNIQUE KEY\s+|WITH UNIQUE KEY\s+)",
        r"\bDATA\s*:\s*([A-Z][A-Z0-9_]+)\s+(?:TYPE)\s+[A-Z][A-Z0-9_~\-]+(?:WITH NON-UNIQUE KEY\s+|WITH UNIQUE KEY\s+)",
        r"\bDATA\s+([A-Z][A-Z0-9_]+)\s+(?:TYPE)\s+(?:RANGE OF\s+|TABLE OF\s+ )?WITH HEADER LINE\s+",
        r"\bDATA\s*([A-Z][A-Z0-9_]+)\s+(?:TYPE)\s+(?:RANGE OF\s+|TABLE OF\s+ )?WITH HEADER LINE\s+",
        r"\bDATA\s+([A-Z][A-Z0-9_]+)\s+(?:LIKE|TYPE)\s+[A-Z][A-Z0-9_~\-]+\s+OCCURS\s+0",
        r"\bDATA\s*:\s*([A-Z][A-Z0-9_]+)\s+(?:LIKE|TYPE)\s+[A-Z][A-Z0-9_~\-]+\s+OCCURS\s+0",
        r"\bDATA\s+([A-Z][A-Z0-9_]+)\s+OCCURS\s+0",
        r"\bDATA\s*:\s*([A-Z][A-Z0-9_]+)\s+OCCURS\s+0",
        r"\bBEGIN\s+OF\s+([A-Z][A-Z0-9_]+)\s+OCCURS\s+0",
        r"\bINTO\s+TABLE\s+@DATA\(([A-Z][A-Z0-9_]+)\)",
        r"\bDATA\(([A-Z][A-Z0-9_]+)\)\s*=\s*VALUE\s+",
        r"\bDATA\s+([A-Z][A-Z0-9_]+)\s+TYPE\s+(?:[A-Z][A-Z0-9_]+)",
        r"\bDATA\s*:\s*([A-Z][A-Z0-9_]+)\s+TYPE\s+(?:[A-Z][A-Z0-9_]+)",
        r",\s*([A-Z][A-Z0-9_]+)\s+(?:TYPE|LIKE)\s+(?:STANDARD\s+|SORTED\s+|HASHED\s+)?TABLE\s+OF",
        r",\s*([A-Z][A-Z0-9_]+)\s+(?:LIKE|TYPE)\s+[A-Z][A-Z0-9_~\-]+\s+OCCURS\s+0",
        r",\s*([A-Z][A-Z0-9_]+)\s+OCCURS\s+0",
        r"\bDATA\s+([LGIERC]T_[A-Z0-9_]+)\b",
        r"\bDATA\s*:\s*([LGIERC]T_[A-Z0-9_]+)\b",
        r",\s*([LGIERC]T_[A-Z0-9_]+)\b"
    ]

    occurrences = []
    for pattern in patterns:
        for match in re.finditer(pattern, code_no_strings, flags=re.IGNORECASE):
            occurrences.append((match.start(), match.group(1)))
    occurrences.sort(key=lambda x: x[0])

    tables = []
    for _, token in occurrences:
        token = token.upper()
        if is_internal_table_name(token):
            tables.append(token)

    return unique_preserve_order(tables)


def is_internal_table_name(token: str):
    if not token:
        return False
    token = token.upper().strip()
    return token.startswith(("GT_", "LT_", "IT_", "ET_", "RT_", "CT_"))


def extract_classes(code: str):
    classes = re.findall(r"\bCLASS\s+([A-Z0-9_]+)\s+(?:DEFINITION|IMPLEMENTATION)\b", code, flags=re.IGNORECASE)
    return unique_preserve_order([c.upper() for c in classes])


# --- User-required functions for extracting methods and method calls
def extract_methods(code: str) -> List[str]:
    methods = []
    # Pattern 1: METHOD method_name (implementation) - negative lookbehind to avoid CALL METHOD
    pattern1 = r"(?<!CALL\s)\bMETHOD\s+([A-Z0-9_]+)\b"
    matches = re.findall(pattern1, code, flags=re.IGNORECASE)
    methods.extend(matches)
    # Pattern 2: METHODS method_name1, method_name2 (declaration, optional colon and commas)
    pattern2 = r"\bMETHODS\s*:?\s*((?:[A-Z0-9_]+\s*(?:,\s*|FOR\s+|EXPORTING\s+|IMPORTING\s+|CHANGING\s+|RETURNING\s+|EXCEPTIONS\s+|RAISING\s+|TYPE\s+|LIKE\s+|VALUE\s+|DEFAULT\s+|OPTIONAL\s+|REF\s+TO\s+|TYPE\s+REF\s+TO\s+))*)"
    for match in re.finditer(pattern2, code, flags=re.IGNORECASE | re.DOTALL):
        part = match.group(1)
        tokens = re.split(r",|\s+FOR\s+|\s+EXPORTING\s+|\s+IMPORTING\s+|\s+CHANGING\s+|\s+RETURNING\s+|\s+EXCEPTIONS\s+|\s+RAISING\s+|\s+TYPE\s+|\s+LIKE\s+|\s+VALUE\s+|\s+DEFAULT\s+|\s+OPTIONAL\s+|\s+REF\s+TO\s+|\s+TYPE\s+REF\s+TO\s+", part, flags=re.IGNORECASE)
        for token in tokens:
            token = token.strip()
            if re.match(r"^[A-Z0-9_]+$", token, flags=re.IGNORECASE):
                methods.append(token)
    # Pattern 3: CLASS-METHODS method_name1, method_name2 (static declarations)
    pattern3 = r"\bCLASS-METHODS\s*:?\s*((?:[A-Z0-9_]+\s*(?:,\s*|FOR\s+|EXPORTING\s+|IMPORTING\s+|CHANGING\s+|RETURNING\s+|EXCEPTIONS\s+|RAISING\s+|TYPE\s+|LIKE\s+|VALUE\s+|DEFAULT\s+|OPTIONAL\s+|REF\s+TO\s+|TYPE\s+REF\s+TO\s+))*)"
    for match in re.finditer(pattern3, code, flags=re.IGNORECASE | re.DOTALL):
        part = match.group(1)
        tokens = re.split(r",|\s+FOR\s+|\s+EXPORTING\s+|\s+IMPORTING\s+|\s+CHANGING\s+|\s+RETURNING\s+|\s+EXCEPTIONS\s+|\s+RAISING\s+|\s+TYPE\s+|\s+LIKE\s+|\s+VALUE\s+|\s+DEFAULT\s+|\s+OPTIONAL\s+|\s+REF\s+TO\s+|\s+TYPE\s+REF\s+TO\s+", part, flags=re.IGNORECASE)
        for token in tokens:
            token = token.strip()
            if re.match(r"^[A-Z0-9_]+$", token, flags=re.IGNORECASE):
                methods.append(token)
    # Filter out false positives
    forbidden = {
        "FOR", "EVENT", "OF", "RETURNING", "EXPORTING", "IMPORTING", "CHANGING", 
        "EXCEPTIONS", "VALUE", "TYPE", "LIKE", "OPTIONAL", "DEFAULT", "RAISING",
        "PRINT_TOP_OF_LIST", "PRINT_END_OF_PAGE"
    }
    bad_substrings = ("GRID", "CONTAINER", "ALV", "CONTROL")
    filtered = []
    for m in methods:
        upper_m = m.upper()
        if upper_m in forbidden:
            continue
        if any(sub in upper_m for sub in bad_substrings):
            continue
        filtered.append(upper_m)
    return unique_preserve_order(filtered)


def extract_method_calls_and_handlers(code: str) -> Tuple[List[str], List[str]]:
    method_calls = []
    handler_registrations = []
    # Pattern 1: CALL METHOD object->method or class=>method
    pattern1 = r"\bCALL\s+METHOD\s+(?:[A-Z0-9_]+->|[A-Z0-9_]+=>|\([^\)]+\)->|\([^\)]+\)=>)([A-Z0-9_]+)\b"
    matches = re.findall(pattern1, code, flags=re.IGNORECASE)
    method_calls.extend(matches)
    # Pattern 2: object->method(...) or class=>method(...)
    pattern2 = r"\b(?:[A-Z0-9_]+->|[A-Z0-9_]+=>|\([^\)]+\)->|\([^\)]+\)=>)([A-Z0-9_]+)\s*\("
    matches = re.findall(pattern2, code, flags=re.IGNORECASE)
    method_calls.extend(matches)
    # Pattern3: object->method. or class=>method.
    pattern3 = r"\b(?:[A-Z0-9_]+->|[A-Z0-9_]+=>|\([^\)]+\)->|\([^\)]+\)=>)([A-Z0-9_]+)\s*\."
    matches = re.findall(pattern3, code, flags=re.IGNORECASE)
    method_calls.extend(matches)
    # Pattern4: SET HANDLER
    pattern4 = r"\bSET\s+HANDLER\s+(?:[A-Z0-9_]+->|[A-Z0-9_]+=>)?([A-Z0-9_]+)(?:\s+FOR|\s*[,.:])?"
    matches = re.findall(pattern4, code, flags=re.IGNORECASE)
    handler_registrations.extend(matches)
    # Filter out false positives for both
    bad_substrings = ("GRID", "CONTAINER", "ALV", "CONTROL")
    filtered_calls = []
    for c in method_calls:
        upper_c = c.upper()
        if any(sub in upper_c for sub in bad_substrings):
            continue
        filtered_calls.append(upper_c)
    filtered_handlers = []
    for h in handler_registrations:
        upper_h = h.upper()
        if any(sub in upper_h for sub in bad_substrings):
            continue
        filtered_handlers.append(upper_h)
    return unique_preserve_order(filtered_calls), unique_preserve_order(filtered_handlers)
