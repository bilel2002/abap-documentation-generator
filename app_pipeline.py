import streamlit as st
import ollama
import json
import re
import threading
import time
from collections import Counter

def enrich_json(parsed_data):
    """Step 1: Enrich the JSON data"""
    enriched = {
        "forms": parsed_data.get("forms", []),
        "sap_tables_used": parsed_data.get("sap_tables_used", []),
        "internal_tables": parsed_data.get("internal_tables", [])
    }
    
    # Enrich performs
    performs = parsed_data.get("performs", [])
    perform_counts = Counter(performs)
    enriched_performs = []
    for form, count in perform_counts.items():
        positions = []
        pattern = re.compile(rf'\bPERFORM\s+{re.escape(form)}\b', re.IGNORECASE)
        enriched_performs.append({
            "form": form,
            "call_count": count,
            "called_at_positions": positions
        })
    enriched["performs"] = enriched_performs
    
    # Enrich function calls
    function_calls = parsed_data.get("function_calls", [])
    func_counts = Counter(function_calls)
    enriched_funcs = []
    for func, count in func_counts.items():
        positions = []
        pattern = re.compile(rf'\bCALL\s+FUNCTION\s+[\'"]?{re.escape(func)}[\'"]?', re.IGNORECASE)
        enriched_funcs.append({
            "function": func,
            "call_count": count,
            "called_at_positions": positions
        })
    enriched["function_calls"] = enriched_funcs
    
    # Deduplicate selects
    selects = parsed_data.get("selects", [])
    seen = set()
    deduplicated_selects = []
    for select in selects:
        key = (
            select.get("table", ""),
            tuple(sorted(select.get("fields", []))),
            tuple(sorted(select.get("into", {}).get("targets", [])))
        )
        if key not in seen:
            seen.add(key)
            deduplicated_selects.append(select)
    enriched["selects"] = deduplicated_selects
    
    return enriched

def extract_form_bodies(raw_code, forms):
    """Step 2: Extract form bodies from raw ABAP"""
    form_bodies = {}
    for form_name in forms:
        pattern = re.compile(
            rf'\bFORM\s+{re.escape(form_name)}\b.*?\bENDFORM\b',
            re.IGNORECASE | re.DOTALL
        )
        match = pattern.search(raw_code)
        if match:
            body = match.group(0)
            lines = body.split('\n')
            if len(lines) > 80:
                # Trim if more than 80 lines
                trimmed = lines[:60] + [f"({len(lines) - 80} lines trimmed)"] + lines[-20:]
                form_bodies[form_name] = '\n'.join(trimmed)
            else:
                form_bodies[form_name] = body
        else:
            form_bodies[form_name] = "FORM body not found in code"
    return form_bodies

def filter_context_per_form(form_name, form_body, enriched_data):
    """Step 3: Filter relevant context per form"""
    functions_in_body = []
    tables_in_body = []
    select_fields_in_body = []
    
    # Find functions called in this form
    for func in enriched_data.get("function_calls", []):
        func_name = func.get("function", "")
        if re.search(rf'\bCALL\s+FUNCTION\s+[\'"]?{re.escape(func_name)}[\'"]?', form_body, re.IGNORECASE):
            functions_in_body.append(func)
    
    # Find SAP tables referenced in this form
    for table in enriched_data.get("sap_tables_used", []):
        if re.search(rf'\b{re.escape(table)}\b', form_body, re.IGNORECASE):
            tables_in_body.append(table)
    
    # Find SELECTs that use tables in this form
    relevant_selects = []
    for select in enriched_data.get("selects", []):
        select_table = select.get("table", "")
        if select_table in tables_in_body:
            relevant_selects.append(select)
        
        # Check if SELECT targets are referenced
        for target in select.get("into", {}).get("targets", []):
            if re.search(rf'\b{re.escape(target)}\b', form_body, re.IGNORECASE):
                if select not in relevant_selects:
                    relevant_selects.append(select)
    
    # Find performs/calls for this form
    perform_info = next((p for p in enriched_data.get("performs", []) if p.get("form") == form_name), None)
    
    return {
        "form": form_name,
        "form_body": form_body,
        "perform_info": perform_info,
        "relevant_functions": functions_in_body,
        "relevant_tables": tables_in_body,
        "relevant_selects": relevant_selects
    }

def generate_form_doc(form_context, timeout_seconds=60):
    """Generate documentation for one form with timeout"""
    result = [None]
    
    def model_call():
        try:
            prompt = f"""You are an expert ABAP documentation specialist. 
Write clear, structured documentation for this ABAP FORM.

FORM NAME: {form_context['form']}

CALL INFO: {json.dumps(form_context['perform_info'], indent=2) if form_context['perform_info'] else 'Not called by any PERFORMs'}

RELEVANT FUNCTIONS CALLED: {json.dumps([f.get('function') for f in form_context['relevant_functions']], indent=2) if form_context['relevant_functions'] else 'None'}

RELEVANT SAP TABLES: {', '.join(form_context['relevant_tables']) if form_context['relevant_tables'] else 'None'}

RELEVANT SELECTS: {json.dumps([{'table': s.get('table'), 'fields': s.get('fields', [])} for s in form_context['relevant_selects']], indent=2) if form_context['relevant_selects'] else 'None'}

SOURCE CODE:
```abap
{form_context['form_body']}
```

Please document this FORM concisely and technically. Keep it under 1000 characters.
"""
            
            response = ollama.generate(
                model="mistral:7b-instruct",
                prompt=prompt,
                stream=False,
                options={
                    "temperature": 0.1,
                    "num_predict": 1000,
                    "num_ctx": 4096
                }
            )
            result[0] = response.get("response", "No documentation generated")
        except Exception as e:
            result[0] = f"Error: {str(e)}"
    
    thread = threading.Thread(target=model_call)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        return f"Warning: Documentation generation timed out after {timeout_seconds} seconds"
    else:
        return result[0]

def assemble_documentation(all_docs):
    """Step 5: Assemble final documentation"""
    md_parts = []
    md_parts.append("# ABAP Program Documentation\n")
    
    for form_name, doc_text in all_docs.items():
        md_parts.append(f"\n## FORM: {form_name}\n")
        md_parts.append(doc_text)
        md_parts.append("\n---\n")
    
    return '\n'.join(md_parts)

def main():
    st.set_page_config(page_title="ABAP Form Documentation Pipeline", layout="wide")
    st.title("ABAP Form Documentation Pipeline")
    
    # File uploads
    col1, col2 = st.columns(2)
    with col1:
        abap_file = st.file_uploader("Upload ABAP File (.abap)", type=["abap", "txt"])
    with col2:
        json_file = st.file_uploader("Upload Parsed JSON File", type=["json"])
    
    if abap_file and json_file:
        # Read files
        raw_code = abap_file.read().decode("utf-8")
        parsed_data = json.load(json_file)
        
        # Step 1: Enrich JSON
        if st.button("Generate Documentation"):
            try:
                with st.spinner("Step 1/6: Enriching JSON data..."):
                    enriched_data = enrich_json(parsed_data)
                    st.success("JSON enriched successfully!")
                
                # Step 2: Extract form bodies
                with st.spinner("Step 2/6: Extracting form bodies..."):
                    form_bodies = extract_form_bodies(raw_code, enriched_data["forms"])
                    st.success(f"Extracted {len(form_bodies)} form bodies!")
                
                # Step 3-4: Document each form
                st.subheader("Documenting Forms...")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                all_docs = {}
                total_forms = len(enriched_data["forms"])
                
                for idx, form_name in enumerate(enriched_data["forms"]):
                    status_text.text(f"Processing form: {form_name} ({idx+1}/{total_forms})")
                    
                    # Step 3: Filter context
                    form_body = form_bodies.get(form_name, "")
                    form_context = filter_context_per_form(form_name, form_body, enriched_data)
                    
                    # Step 4: Generate documentation
                    doc_text = generate_form_doc(form_context)
                    all_docs[form_name] = doc_text
                    
                    # Update UI progressively
                    with st.expander(f"## FORM: {form_name}", expanded=False):
                        st.markdown(doc_text)
                    
                    progress_bar.progress((idx + 1) / total_forms)
                    
                    time.sleep(1)
                
                status_text.text("Documentation complete!")
                
                # Step 5: Assemble final documentation
                final_doc = assemble_documentation(all_docs)
                
                # Show and download
                st.subheader("Final Documentation")
                st.markdown(final_doc)
                
                st.download_button(
                    label="Download Documentation",
                    data=final_doc,
                    file_name="abap_form_documentation.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Check the terminal for details")
                import traceback
                st.code(traceback.format_exc())
    else:
        st.info("Please upload both the ABAP file and the parsed JSON file to continue")

if __name__ == "__main__":
    main()