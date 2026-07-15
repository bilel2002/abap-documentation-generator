import streamlit as st
import ollama
import json
import re
import threading
import time
import importlib
import sys
from pathlib import Path
from collections import Counter

# Ensure the core module is in path
if Path(__file__).parent not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

# Import module objects so reload updates what the app actually calls
import core.extractor as extractor
import core.cleaner as cleaner
import core.parser_refactored as parser_refactored
import core.chroma_integration as chroma_integration

# Force reload the working modules and keep the refreshed module objects
extractor = importlib.reload(extractor)
cleaner = importlib.reload(cleaner)
parser_refactored = importlib.reload(parser_refactored)
chroma_integration = importlib.reload(chroma_integration)

# Fixed model configuration
MODEL_NAME = "mistral:7b-instruct"

@st.cache_data
def cached_extract_text(uploaded_file):
    """Cache text extraction to avoid re-reading file on every interaction"""
    return extractor.extract_text(uploaded_file)

@st.cache_data
def cached_clean_text(raw_text):
    """Cache text cleaning"""
    return cleaner.clean_text(raw_text)


def get_parser_cache_version():
    """Invalidate cached parses when the parser file changes."""
    return Path(parser_refactored.__file__).stat().st_mtime_ns

@st.cache_data
def cached_parse_abap(cleaned_text, parser_cache_version):
    """Cache ABAP parsing"""
    return parser_refactored.parse_abap(cleaned_text)

@st.cache_data
def enrich_json(parsed_data):
    """Step 1: Enrich the JSON data (cached)"""
    enriched = {
        "forms": parsed_data.get("forms", []),
        "sap_tables_used": parsed_data.get("sap_tables_used", []),
        "internal_tables": parsed_data.get("internal_tables", []),
        "classes": parsed_data.get("classes", []),
        "methods": parsed_data.get("methods", []),
        "method_calls": parsed_data.get("method_calls", []),
        "set_handler_registrations": parsed_data.get("set_handler_registrations", [])
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

@st.cache_resource
def get_chroma_manager():
    """Cache ChromaABAPManager instance to avoid reinitializing every time"""
    return chroma_integration.ChromaABAPManager()

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
            form_bodies[form_name] = body  # No truncation! Keep full form
        else:
            form_bodies[form_name] = "FORM body not found in code"
    return form_bodies

def extract_includes(raw_code):
    """Extract INCLUDE statements from ABAP code"""
    includes = []
    include_pattern = re.compile(r'INCLUDE\s+([^\s.]+)\.', re.IGNORECASE)
    matches = include_pattern.findall(raw_code)
    return matches

def filter_context_per_form(form_name, form_body, enriched_data, all_form_bodies):
    """Step 3: Filter relevant context per form"""
    functions_in_body = []
    tables_in_body = []
    performs_in_body = []
    internal_tables_in_body = []
    
    # Find all FUNCTION MODULES called in this form
    for func_call in enriched_data.get("function_calls", []):
        func_name = func_call.get("function", "")
        if func_name:
            if re.search(rf'\bCALL\s+FUNCTION\s+[\'"]?{re.escape(func_name)}[\'"]?', form_body, re.IGNORECASE):
                functions_in_body.append(func_call)
    
    # Find all SAP TABLES referenced in this form
    for sap_table in enriched_data.get("sap_tables_used", []):
        if re.search(rf'\b{re.escape(sap_table)}\b', form_body, re.IGNORECASE):
            tables_in_body.append(sap_table)
    
    # Find all PERFORMS called in this form
    for perform in re.findall(r'\bPERFORM\s+(\w+)', form_body, re.IGNORECASE):
        if perform in all_form_bodies:
            performs_in_body.append(perform)
    
    # Find all SELECT statements relevant to this form
    relevant_selects = []
    for select in enriched_data.get("selects", []):
        select_table = select.get("table", "")
        # Check if SELECT table is used in the form
        if select_table in tables_in_body:
            relevant_selects.append(select)
        
        # Check if SELECT targets are referenced in the form
        for target in select.get("into", {}).get("targets", []):
            if re.search(rf'\b{re.escape(target)}\b', form_body, re.IGNORECASE):
                if select not in relevant_selects:
                    relevant_selects.append(select)
    
    # Find all INTERNAL TABLES used in this form
    for internal_table in enriched_data.get("internal_tables", []):
        if re.search(rf'\b{re.escape(internal_table)}\b', form_body, re.IGNORECASE):
            internal_tables_in_body.append(internal_table)
    
    # Find info about this form being called elsewhere
    perform_info = next((p for p in enriched_data.get("performs", []) if p.get("form") == form_name), None)
    
    return {
        "form": form_name,
        "form_body": form_body,
        "perform_info": perform_info,
        "relevant_functions": functions_in_body,
        "relevant_tables": tables_in_body,
        "relevant_selects": relevant_selects,
        "performs_called": performs_in_body,
        "internal_tables_used": internal_tables_in_body
    }

def generate_form_doc(form_context, rag_context=None, timeout_seconds=180, model_name="llama3.2:latest", temperature=0.1):
    """Generate documentation for one form with timeout"""
    # Build system prompt (in French)
    system_prompt = """Vous êtes un spécialiste senior de la documentation technique SAP ABAP avec 15 ans d'expérience dans la documentation des systèmes SAP d'entreprise.

Votre style de documentation doit être:
- Précis et technique — utilisez la terminologie ABAP et SAP correcte
- Honnête — si quelque chose ne peut pas être déterminé à partir du code fourni, dites-le explicitement
- Structuré — suivez toujours le format de documentation exact demandé
- Concis — pas de phrases de remplissage, chaque ligne doit ajouter de la valeur

Vous comprenez:
- La syntaxe ABAP: FORM/ENDFORM, PERFORM, FUNCTION MODULES, appels BAPI, instructions SELECT
- Les tables standard SAP: ce qu'elles stockent et leur signification métier (KNB1, EKKO, EKPO, VBAK, MARA etc.)
- Les conventions de nommage ABAP: les préfixes iv_, ev_, lv_, lt_, ls_, gt_, gs_, wa_, t_ et ce qu'ils signifient
- Les processus métier SAP: approvisionnement, ventes, gestion de la qualité, finance, logistique

RÈGLES STRICTES à respecter:
- Ne jamais inventer de noms de paramètres, de tables ou de logique qui ne sont pas présents dans le code fourni
- Ne jamais supposer ce que contient une variable à moins que son nom ou son utilisation ne le rende explicite
- Si le code source a été tronqué, reconnaissez que certaines logiques peuvent ne pas être visibles
- Utilisez toujours le nom exact du FORM, des tables et des modules de fonction tels que fournis
- Lorsque vous documentez un module de fonction standard SAP (non-Z), expliquez brièvement ce qu'il fait dans SAP
- Lorsque vous documentez une fonction Z personnalisée, ne documentez que ce que le code reveals
"""
    # Build main prompt parts (in French)
    prompt_parts = [
        "Vous êtes un développeur ABAP expert et un spécialiste de la documentation technique.",
        "Votre tâche est de créer une documentation détaillée et précise pour le FORM ABAP suivant.",
        "IMPORTANT: Ne PAS inventer d'informations - utilisez uniquement ce qui est fourni dans le contexte ci-dessous.",
        "Si vous n'êtes pas sûr de quelque chose, indiquez explicitement qu'il n'a pas pu être déterminé à partir du code fourni.",
        "",
        f"## NOM DU FORM: {form_context['form']}",
        "",
        "## INFORMATIONS D'APPEL:",
        json.dumps(form_context['perform_info'], indent=2) if form_context['perform_info'] else "Ce FORM n'est pas appelé par d'autres instructions PERFORM.",
        "",
        "## MODULES DE FONCTION APPELÉS DANS CE FORM:",
        json.dumps([f.get('function') for f in form_context['relevant_functions']], indent=2) if form_context['relevant_functions'] else "Aucun module de fonction n'est appelé.",
        "",
        "## TABLES SAP ACCÉDÉES DANS CE FORM:",
        ", ".join(form_context['relevant_tables']) if form_context['relevant_tables'] else "Aucune table SAP n'est accédée directement.",
        "",
        "## TABLES INTERNES UTILISÉES DANS CE FORM:",
        ", ".join(form_context['internal_tables_used']) if form_context['internal_tables_used'] else "Aucune table interne n'est utilisée.",
        "",
        "## AUTRES FORMS APPELÉS DANS CE FORM:",
        ", ".join(form_context['performs_called']) if form_context['performs_called'] else "Aucun autre FORM n'est appelé.",
        "",
        "## INSTRUCTIONS SELECT DANS CE FORM:",
        json.dumps([{
            'table': s.get('table'),
            'fields': s.get('fields', []),
            'condition': s.get('condition', ''),
            'into': s.get('into', {})
        } for s in form_context['relevant_selects']], indent=2) if form_context['relevant_selects'] else "Aucune instruction SELECT."
    ]
    
    # Add RAG context if available
    if rag_context:
        prompt_parts.extend([
            "",
            "## ADDITIONAL RELATED CODE (From RAG Search):",
            rag_context
        ])
    
    # Add source code and final instructions (in French)
    prompt_parts.extend([
        "",
        "## CODE SOURCE:",
        "```abap",
        form_context['form_body'],
        "```",
        "",
        "Veuillez créer une documentation structurée avec:",
        "1. Objectif: Que fait ce form? Quel problème résout-il?",
        "2. Paramètres d'entrée: Quels paramètres sont passés? A quoi servent-ils?",
        "3. Paramètres de sortie: Quels paramètres sont renvoyés? Que contiennent-ils?",
        "4. Logique clé: Description étape par étape de ce que fait le code",
        "5. Dépendances: De quels autres forms, modules de fonction ou tables dépend-il?",
        "",
        "Gardez votre documentation détaillée mais claire. Concentrez-vous sur la précision technique. Ne PAS inventer d'informations."
    ])
    
    full_prompt = f"{system_prompt}\n\n{chr(10).join(prompt_parts)}"
    
    try:
        client = ollama.Client(timeout=timeout_seconds)
        response = client.generate(
            model=model_name,
            prompt=full_prompt,
            stream=False,
            options={
                "temperature": temperature,
                "num_predict": 3000,
                "num_ctx": 8192
            }
        )
        return response.get("response", "No documentation generated")
    except Exception as e:
        return f"Error: {str(e)}"


def generate_program_documentation(full_abap_code, enriched_data, rag_context=None, timeout_seconds=180, model_name="llama3.2:latest", temperature=0.1):
    """Generate documentation for the entire ABAP program."""
    # Build system prompt (in French)
    system_prompt = """Vous êtes un spécialiste senior de la documentation technique SAP ABAP avec 15 ans d'expérience dans la documentation des systèmes SAP d'entreprise.

Votre style de documentation doit être:
- Précis et technique — utilisez la terminologie ABAP et SAP correcte
- Honnête — si quelque chose ne peut pas être déterminé à partir du code fourni, dites-le explicitement
- Structuré — suivez toujours le format de documentation exact demandé
- Concis — pas de phrases de remplissage, chaque ligne doit ajouter de la valeur

Vous comprenez:
- La syntaxe ABAP: FORM/ENDFORM, PERFORM, FUNCTION MODULES, appels BAPI, instructions SELECT
- Les tables standard SAP: ce qu'elles stockent et leur signification métier (KNB1, EKKO, EKPO, VBAK, MARA etc.)
- Les conventions de nommage ABAP: les préfixes iv_, ev_, lv_, lt_, ls_, gt_, gs_, wa_, t_ et ce qu'ils signifient
- Les processus métier SAP: approvisionnement, ventes, gestion de la qualité, finance, logistique

RÈGLES STRICTES à respecter:
- Ne jamais inventer de noms de paramètres, de tables ou de logique qui ne sont pas présents dans le code fourni
- Ne jamais supposer ce que contient une variable à moins que son nom ou son utilisation ne le rende explicite
- Si le code source a été tronqué, reconnaissez que certaines logiques peuvent ne pas être visibles
- Utilisez toujours le nom exact du FORM, des tables et des modules de fonction tels que fournis
- Lorsque vous documentez un module de fonction standard SAP (non-Z), expliquez brièvement ce qu'il fait dans SAP
- Lorsque vous documentez une fonction Z personnalisée, ne documentez que ce que le code reveals
"""
    # Build main prompt parts (in French)
    prompt_parts = [
        "Vous êtes un développeur ABAP expert et un spécialiste de la documentation technique.",
        "Votre tâche est de créer une documentation complète pour ce programme ABAP entier.",
        "IMPORTANT: Ne PAS inventer d'informations - utilisez uniquement ce qui est fourni dans le contexte ci-dessous.",
        "",
        f"## APERÇU DU PROGRAMME",
        "",
        f"## TOUS LES FORMS DU PROGRAMME: {', '.join(enriched_data.get('forms', []))}",
        "",
        f"## CLASSES DÉFINIES/UTILISÉES: {', '.join(enriched_data.get('classes', [])) if enriched_data.get('classes') else 'Aucune'}",
        "",
        f"## MÉTHODES DÉFINIES/UTILISÉES: {', '.join(enriched_data.get('methods', [])) if enriched_data.get('methods') else 'Aucune'}",
        "",
        f"## TABLES SAP UTILISÉES: {', '.join(enriched_data.get('sap_tables_used', []))}",
        "",
        f"## TABLES INTERNES: {', '.join(enriched_data.get('internal_tables', []))}",
        "",
        f"## MODULES DE FONCTION APPELÉS: {', '.join([f.get('function') for f in enriched_data.get('function_calls', [])])}",
        "",
    ]
    
    # Add RAG context if available
    if rag_context:
        prompt_parts.extend([
            "",
            "## ADDITIONAL SAP KNOWLEDGE:",
            rag_context
        ])
    
    # Add full source code and final instructions (in French)
    prompt_parts.extend([
        "",
        "## CODE SOURCE ABAP COMPLET:",
        "```abap",
        full_abap_code,
        "```",
        "",
        "Veuillez créer une documentation structurée pour LE PROGRAMME ENTIER avec:",
        "1. Objectif du programme: Que fait ce programme globalement? Quel problème métier résout-il?",
        "2. Flux logique de haut niveau: Quel est le flux d'exécution étape par étape du début à la fin?",
        "3. Structures de données clés: Quelles sont les principales tables internes et structures utilisées?",
        "4. Notes techniques: Y a-t-il des détails techniques importants (jointures, considérations de performance, techniques spéciales utilisées)?",
        "",
        "Gardez votre documentation détaillée mais claire. Concentrez-vous sur la précision technique. Ne PAS inventer d'informations."
    ])
    
    full_prompt = f"{system_prompt}\n\n{chr(10).join(prompt_parts)}"
    
    try:
        client = ollama.Client(timeout=timeout_seconds)
        response = client.generate(
            model=model_name,
            prompt=full_prompt,
            stream=False,
            options={
                "temperature": temperature,
                "num_predict": 3000,
                "num_ctx": 8192
            }
        )
        return response.get("response", "No program documentation generated")
    except Exception as e:
        return f"Error generating program doc: {str(e)}"


def assemble_documentation(program_doc, all_docs):
    """Step 5: Assemble final documentation."""
    md_parts = []
    md_parts.append("# Documentation de code ABAP\n")
    
    # Add program-level documentation FIRST
    if program_doc:
        md_parts.append("\n---\n")
        md_parts.append("## Documentation complete\n")
        md_parts.append(program_doc)
        md_parts.append("\n---\n")
    
    # Then add form-by-form documentation
    for form_name, doc_text in all_docs.items():
        md_parts.append(f"\n## FORM: {form_name}\n")
        md_parts.append(doc_text)
        md_parts.append("\n---\n")

    
    return '\n'.join(md_parts)


def main():
    # Page configuration with SAP-inspired theme
    st.set_page_config(
        page_title="Générateur de Documentation ABAP",
        page_icon="🧑‍💻",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar configuration
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color: #0F4C81; margin-bottom: 0;'>🧑‍💻 ABAP Doc</h1>
            <p style='color: #64748B; font-size: 0.9rem; margin-top: 0;'>Générateur automatique</p>
        </div>
        """, unsafe_allow_html=True)
 
        
        st.divider()
        
        st.subheader("📊 État système")
        sap_kb_path = Path(__file__).parent / "sap_knowledge_base.json"
        if sap_kb_path.exists():
            st.success("✅ Base SAP OK")
        else:
            st.warning("⚠️ Base SAP absente")
        
        st.markdown("---")
        
      

    # Main content
    st.title("📚 Générateur de Documentation ABAP")
    st.markdown("Téléchargez votre code ABAP et obtenez une documentation technique complète automatiquement.")

    # File upload section
    st.divider()
    uploaded_file = st.file_uploader(
        "📁 Téléchargez votre fichier ABAP / TXT / PDF",
        type=["abap", "txt", "pdf"],
        help="Formats supportés : .abap, .txt, .pdf"
    )

    if uploaded_file:
        # Create tabs for better organization
        tab_input, tab_analysis, tab_docs, tab_chatbot = st.tabs(["📄 Entrée", "🔍 Analyse", "📚 Documentation", "🤖 Chatbot"])

        # ===== TAB 1: INPUT =====
        with tab_input:
            st.header("Code source")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Texte brut")
                raw_text = cached_extract_text(uploaded_file)
                if raw_text and raw_text.strip():
                    st.code(raw_text[:5000] + ("..." if len(raw_text) > 5000 else ""), language="abap")
                else:
                    st.warning("Aucun texte n'a pu être extrait.")
            
            with col2:
                st.subheader("Texte nettoyé")
                cleaned_text = cached_clean_text(raw_text) if raw_text else ""
                if cleaned_text and cleaned_text.strip():
                    st.code(cleaned_text[:5000] + ("..." if len(cleaned_text) > 5000 else ""), language="abap")
                else:
                    st.warning("Aucun texte à nettoyer.")

        if not raw_text or not raw_text.strip():
            st.stop()

        # ===== TAB 2: ANALYSIS =====
        with tab_analysis:
            st.header("Analyse du code")
            
            parsed_data = cached_parse_abap(cleaned_text, get_parser_cache_version())
            
            # Summary metrics with nicer, spaced-out styling
            st.subheader("📊 Résumé rapide")
            
            # Row 1: Program structure
            st.subheader("📝 Structure du programme")
            row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
            with row1_col1:
                st.metric(
                    label="Forms",
                    value=len(parsed_data.get("forms", [])),
                    delta=f"{len(parsed_data.get('forms', []))} formulaires"
                )
            with row1_col2:
                st.metric(
                    label="Performs",
                    value=len(parsed_data.get("performs", [])),
                    delta=f"{len(parsed_data.get('performs', []))} appels"
                )
            with row1_col3:
                st.metric(
                    label="Selects",
                    value=len(parsed_data.get("selects", [])),
                    delta=f"{len(parsed_data.get('selects', []))} requêtes"
                )
            with row1_col4:
                st.metric(
                    label="Fonctions",
                    value=len(parsed_data.get("function_calls", [])),
                    delta=f"{len(parsed_data.get('function_calls', []))} modules"
                )
            
            st.divider()
            
            # Row 2: Data and classes
            st.subheader("🗄️ Données et classes")
            row2_col1, row2_col2, row2_col3 = st.columns(3)
            with row2_col1:
                st.metric(
                    label="Tables SAP",
                    value=len(parsed_data.get("sap_tables_used", [])),
                    delta=f"{len(parsed_data.get('sap_tables_used', []))} tables"
                )
            with row2_col2:
                st.metric(
                    label="Tables internes",
                    value=len(parsed_data.get("internal_tables", [])),
                    delta=f"{len(parsed_data.get('internal_tables', []))} structures"
                )
            with row2_col3:
                st.metric(
                    label="Classes",
                    value=len(parsed_data.get("classes", [])),
                    delta=f"{len(parsed_data.get('classes', []))} classes"
                )
            
            st.divider()
            
            # Row3: Methods and handlers
            st.subheader("⚙️ Méthodes et gestionnaires d'événements")
            row3_col1, row3_col2, row3_col3 = st.columns(3)
            with row3_col1:
                st.metric(
                    label="Méthodes",
                    value=len(parsed_data.get("methods", [])),
                    delta=f"{len(parsed_data.get('methods', []))} méthodes"
                )
            with row3_col2:
                st.metric(
                    label="Appels de méthodes",
                    value=len(parsed_data.get("method_calls", [])),
                    delta=f"{len(parsed_data.get('method_calls', []))} appels"
                )
            with row3_col3:
                st.metric(
                    label="SET HANDLER",
                    value=len(parsed_data.get("set_handler_registrations", [])),
                    delta=f"{len(parsed_data.get('set_handler_registrations', []))} enregistrements"
                )
            
            st.divider()
            
            # Parsed JSON data
            with st.expander("🔍 Voir les données analysées (JSON)", expanded=False):
                st.json(parsed_data)
                json_str = json.dumps(parsed_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Télécharger JSON",
                    data=json_str,
                    file_name="parsed_abap.json",
                    mime="application/json"
                )

        # ===== TAB 3: DOCUMENTATION =====
        with tab_docs:
            st.header("Génération de la documentation")
            
            if st.button("🚀 Générer la documentation", type="primary", use_container_width=True):
                try:
                    # Initialize sidebar progress tracking
                    st.session_state.progress_forms = []
                    st.session_state.program_doc_done = False
                    
                    with st.sidebar:
                        st.divider()
                        st.subheader("📊 Progression de la génération")
                        
                        # Program doc placeholder
                        program_placeholder = st.empty()
                        program_placeholder.info("🔄 En attente de la documentation du programme...")
                        
                        # Forms placeholders dictionary
                        form_placeholders = {}
                        
                    # Initialize dynamic display area in the main tab
                    st.divider()
                    st.header("Documentation en cours...")
                    # Placeholder for program doc
                    program_display = st.empty()
                    # Placeholder container for forms (list of placeholders)
                    form_display_container = st.container()
                    form_displays = {}
                    
                    # Step 1: Enrich data
                    with st.status("🔄 Étape 1/6 - Enrichissement des données...", expanded=True) as status:
                        enriched_data = enrich_json(parsed_data)
                        status.update(label="✅ Données enrichies", state="complete", expanded=False)
                        time.sleep(0.5)

                    # Step 2: Extract form bodies
                    with st.status("🔄 Étape 2/6 - Extraction des forms...", expanded=True) as status:
                        form_bodies = extract_form_bodies(cleaned_text, enriched_data["forms"])
                        status.update(label=f"✅ {len(form_bodies)} forms extraits", state="complete", expanded=False)
                        time.sleep(0.5)

                    # Step 3: Index into ChromaDB
                    with st.status("🔄 Étape 3/6 - Indexation dans la base de connaissances...", expanded=True) as status:
                        chroma_manager = get_chroma_manager()
                        chroma_manager.reset_session_data()  # Clear only session code and doc data
                        num_code = chroma_manager.index_parsed_data(parsed_data, cleaned_text)
                        
                        # Only index SAP KB if it's not already indexed in the collection
                        if not chroma_manager.is_sap_kb_indexed():
                            status.update(label="🔄 Étape 3/6 - Indexation de la base SAP (première fois)...", state="running")
                            num_sap = chroma_manager.index_sap_knowledge_base()
                        else:
                            num_sap = 0
                            
                        total_indexed = num_code + num_sap
                        if num_sap > 0:
                            status.update(label=f"✅ {total_indexed} éléments indexés (Base SAP incluse)", state="complete", expanded=False)
                        else:
                            status.update(label=f"✅ {num_code} éléments de code indexés (Base SAP réutilisée)", state="complete", expanded=False)
                        time.sleep(0.5)

                    # Step 4: Generate program-level doc
                    with st.status("🔄 Étape 4/6 - Génération documentation programme...", expanded=True) as status:
                        # Update sidebar to show program doc in progress
                        with st.sidebar:
                            program_placeholder.warning("🔄 Génération de la documentation du programme...")
                        
                        program_rag_results = chroma_manager.query_relevant_elements(
                            query_text=f"ABAP program overview and all SAP tables, fields, functions",
                            n_results=30
                        )
                        
                        program_rag_parts = []
                        program_sap_knowledge = [r for r in program_rag_results if r['metadata'].get('source') == 'sap_knowledge_base']
                        program_abap_code = [r for r in program_rag_results if r['metadata'].get('source') != 'sap_knowledge_base']
                        
                        if program_sap_knowledge:
                            program_rag_parts.append("## SAP Knowledge Base References:")
                            for r in program_sap_knowledge:
                                name = r['metadata'].get('table', r['metadata'].get('field', 'Unknown'))
                                type_ = r['metadata'].get('type', 'sap_info')
                                program_rag_parts.append(f"### {type_}: {name}")
                                program_rag_parts.append(r['document'])
                                program_rag_parts.append("---")
                        
                        if program_abap_code:
                            program_rag_parts.append("## Related ABAP Code:")
                            for r in program_abap_code:
                                name = r['metadata'].get('name', r['metadata'].get('table', 'Unknown'))
                                type_ = r['metadata'].get('type', 'code')
                                program_rag_parts.append(f"### {type_}: {name}")
                                program_rag_parts.append(r['document'])
                                program_rag_parts.append("---")
                        
                        program_rag_context = "\n".join(program_rag_parts) if program_rag_parts else ""
                        
                        program_doc = generate_program_documentation(
                cleaned_text, 
                enriched_data, 
                rag_context=program_rag_context,
                timeout_seconds=240,
                model_name=MODEL_NAME,
            )
                        st.session_state.program_doc_done = True
                        status.update(label="✅ Documentation programme générée", state="complete", expanded=False)
                        
                        # Update sidebar to mark program doc as done
                        with st.sidebar:
                            program_placeholder.success("✅ Documentation du programme terminée")
                        
                        # Display program doc immediately
                        with program_display.container():
                            st.subheader("📄 Documentation du programme principal")
                            st.markdown(program_doc)

                    # Step 5: Generate form docs
                    with st.status("🔄 Étape 5/6 - Génération documentation forms...", expanded=True) as status:
                        all_docs = {}
                        total_forms = len(enriched_data["forms"])
                        progress_bar = st.progress(0)
                        
                        # Initialize form placeholders in sidebar first
                        with st.sidebar:
                            st.subheader("📝 Forms")
                            for form_name in enriched_data["forms"]:
                                form_placeholders[form_name] = st.empty()
                                form_placeholders[form_name].info(f"⏳ En attente: {form_name}")
                        
                        # Initialize form display placeholders in main area
                        with form_display_container:
                            for form_name in enriched_data["forms"]:
                                form_displays[form_name] = st.empty()
                                
                        # Prepare the tasks (Chroma query runs sequentially)
                        tasks = []
                        for form_name in enriched_data["forms"]:
                            form_body = form_bodies.get(form_name, "")
                            form_context = filter_context_per_form(form_name, form_body, enriched_data, form_bodies)
                            
                            rag_results = chroma_manager.query_relevant_elements(
                                query_text=f"ABAP form {form_name} and related SAP tables, fields, functions",
                                n_results=30
                            )
                            
                            sap_knowledge = []
                            abap_code = []
                            for r in rag_results:
                                if r['metadata'].get('source') == 'sap_knowledge_base':
                                    sap_knowledge.append(r)
                                else:
                                    abap_code.append(r)
                            
                            rag_parts = []
                            if sap_knowledge:
                                rag_parts.append("## SAP Knowledge Base References:")
                                for r in sap_knowledge:
                                    name = r['metadata'].get('table', r['metadata'].get('field', 'Unknown'))
                                    type_ = r['metadata'].get('type', 'sap_info')
                                    rag_parts.append(f"### {type_}: {name}")
                                    rag_parts.append(r['document'])
                                    rag_parts.append("---")
                            
                            if abap_code:
                                rag_parts.append("## Related ABAP Code:")
                                for r in abap_code:
                                    name = r['metadata'].get('name', r['metadata'].get('table', 'Unknown'))
                                    type_ = r['metadata'].get('type', 'code')
                                    rag_parts.append(f"### {type_}: {name}")
                                    rag_parts.append(r['document'])
                                    rag_parts.append("---")
                            
                            rag_context = "\n".join(rag_parts) if rag_parts else ""
                            
                            tasks.append({
                                "form_name": form_name,
                                "form_context": form_context,
                                "rag_context": rag_context
                            })
                            
                            with st.sidebar:
                                form_placeholders[form_name].warning(f"🔄 En attente: {form_name}")
                                
                        # Run parallel generation
                        from concurrent.futures import ThreadPoolExecutor, as_completed
                        max_workers = 4
                        
                        with ThreadPoolExecutor(max_workers=max_workers) as executor:
                            future_to_form = {}
                            for task in tasks:
                                form_name = task["form_name"]
                                with st.sidebar:
                                    form_placeholders[form_name].warning(f"🔄 En cours: {form_name}")
                                    
                                future = executor.submit(
                                    generate_form_doc,
                                    task["form_context"],
                                    task["rag_context"],
                                    timeout_seconds=180,
                                    model_name=MODEL_NAME,
                                )
                                future_to_form[future] = form_name
                                
                            completed_count = 0
                            for future in as_completed(future_to_form):
                                form_name = future_to_form[future]
                                try:
                                    doc_text = future.result()
                                except Exception as e:
                                    doc_text = f"Error: {str(e)}"
                                    
                                all_docs[form_name] = doc_text
                                
                                with st.sidebar:
                                    form_placeholders[form_name].success(f"✅ Terminée: {form_name}")
                                    
                                with form_displays[form_name].container():
                                    with st.expander(f"📝 FORM: {form_name}", expanded=False):
                                        st.markdown(doc_text)
                                        
                                completed_count += 1
                                progress_bar.progress(completed_count / total_forms)
                                
                        status.update(label=f"✅ {total_forms} forms documentés", state="complete", expanded=False)

                    # Step 6: Assemble and display
                    with st.status("🔄 Étape 6/6 - Assemblage final...", expanded=True) as status:
                        final_doc = assemble_documentation(program_doc, all_docs)
                        # Store in session state for chatbot
                        st.session_state.generated_documentation = final_doc
                        st.session_state.program_doc = program_doc
                        st.session_state.form_docs = all_docs
                        status.update(label="✅ Documentation terminée !", state="complete", expanded=False)
                        time.sleep(0.5)

                    # Display final documentation
                    st.divider()
                    st.header("Documentation finale")
                    
                    # Download buttons
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.download_button(
                            label="📥 Télécharger en Markdown",
                            data=final_doc,
                            file_name="abap_form_documentation.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    with col2:
                        st.download_button(
                            label="📥 Télécharger en TXT",
                            data=final_doc,
                            file_name="abap_form_documentation.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                    st.divider()
                    
                    # Display documentation with expanders
                    st.subheader("📋 Contenu de la documentation")
                    
                    # Program doc first
                    with st.expander("📄 Documentation du programme principal", expanded=True):
                        st.markdown(program_doc)
                    
                    # Then each form
                    for form_name, doc_text in all_docs.items():
                        with st.expander(f" FORM: {form_name}", expanded=False):
                            st.markdown(doc_text)

                    # Full combined view
                    with st.expander("📚 Voir toute la documentation combinée", expanded=False):
                        st.markdown(final_doc)

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}", icon="🚨")
                    st.info("Vérifiez le terminal pour plus de détails.")
                    import traceback
                    st.code(traceback.format_exc(), language="python")

        # ===== TAB 4: CHATBOT =====
        with tab_chatbot:
            st.title("🤖 Posez vos questions sur la documentation")
            model_name = st.session_state.get("selected_model", "llama3.2:latest")

            # Initialize chat history and context
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Check if we have generated documentation
            has_generated_docs = "generated_documentation" in st.session_state and st.session_state.generated_documentation
            
            if has_generated_docs and ("chat_initialized" not in st.session_state or not st.session_state.chat_initialized):
                # Construct codebase summary for the chatbot
                codebase_summary = f"""## STRUCTURE GLOBALE DU PROGRAMME ABAP ANALYSÉ:
- Nombre de FORMs: {len(parsed_data.get('forms', []))} (Noms: {', '.join(parsed_data.get('forms', [])) if parsed_data.get('forms') else 'Aucun'})
- Nombre d'appels PERFORM: {len(parsed_data.get('performs', []))}
- Nombre de tables SAP accédées: {len(parsed_data.get('sap_tables_used', []))} (Noms: {', '.join(parsed_data.get('sap_tables_used', [])) if parsed_data.get('sap_tables_used') else 'Aucune'})
- Nombre de tables internes: {len(parsed_data.get('internal_tables', []))} (Noms: {', '.join(parsed_data.get('internal_tables', [])) if parsed_data.get('internal_tables') else 'Aucune'})
- Nombre de modules de fonction appelés: {len(parsed_data.get('function_calls', []))} (Noms: {', '.join(parsed_data.get('function_calls', [])) if parsed_data.get('function_calls') else 'Aucun'})
- Nombre de classes: {len(parsed_data.get('classes', []))} (Noms: {', '.join(parsed_data.get('classes', [])) if parsed_data.get('classes') else 'Aucune'})
- Nombre de méthodes: {len(parsed_data.get('methods', []))} (Noms: {', '.join(parsed_data.get('methods', [])) if parsed_data.get('methods') else 'Aucune'})
- Nombre d'appels de méthodes: {len(parsed_data.get('method_calls', []))} (Noms: {', '.join(parsed_data.get('method_calls', [])) if parsed_data.get('method_calls') else 'Aucun'})
- Nombre de SET HANDLER: {len(parsed_data.get('set_handler_registrations', []))} (Noms: {', '.join(parsed_data.get('set_handler_registrations', [])) if parsed_data.get('set_handler_registrations') else 'Aucun'})
"""

                # Create system prompt with global context and generated docs
                system_prompt = f"""Vous êtes un expert senior en développement SAP ABAP avec 15 ans d'expérience.
Votre rôle est de répondre aux questions sur le code source ABAP fourni et sa documentation.

{codebase_summary}

## CONTEXTE DE LA DOCUMENTATION GÉNÉRÉE:
{st.session_state.generated_documentation}

RÈGLES STRICTES À RESPECTER:
1. Répondez UNIQUEMENT en FRANÇAIS.
2. Utilisez les informations de la structure globale, du code source et de la documentation générée ci-dessus pour répondre aux questions.
3. Ne jamais inventer d'informations ou de logique qui ne sont pas présentes dans le contexte.
4. Si une information n'est pas disponible dans le code source ou la documentation, dites-le explicitement sans inventer de réponse.
5. Utilisez la terminologie SAP et ABAP correcte.
6. Soyez précis et technique dans vos réponses.
"""

                # Initialize with system prompt
                st.session_state.messages = [
                    {"role": "system", "content": system_prompt}
                ]
                st.session_state.chat_initialized = True
                # Initialize Chroma manager
                st.session_state.chroma_manager = get_chroma_manager()
                
                # Do NOT clear the entire collection, as that would delete the code elements indexed in Step 3!
                # Instead, just delete previously indexed generated documentation to avoid duplicates
                try:
                    st.session_state.chroma_manager.collection.delete(where={"source": "generated_documentation"})
                except Exception:
                    pass
                
                # Index the generated documentation
                st.session_state.chroma_manager.index_generated_documentation(
                    st.session_state.program_doc,
                    st.session_state.form_docs
                )
            elif not has_generated_docs:
                st.warning("⚠️ Veuillez d'abord générer la documentation dans l'onglet '📚 Documentation' pour utiliser le chatbot!")

            # Display chat messages (skip system prompt in UI)
            if has_generated_docs:
                for message in st.session_state.messages:
                    if message["role"] != "system":
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                # Chat input
                if prompt := st.chat_input("Posez une question sur la documentation ABAP..."):
                    # Add user message to history
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    # Get RAG context for the question
                    with st.spinner("Recherche d'informations pertinentes dans la documentation..."):
                        rag_results = st.session_state.chroma_manager.query_relevant_elements(
                            query_text=prompt,
                            n_results=10
                        )

                        # Prepare RAG context
                        rag_parts = []
                        sap_knowledge = []
                        doc_parts = []
                        code_parts = []
                        for r in rag_results:
                            source = r['metadata'].get('source', '')
                            if source == 'sap_knowledge_base':
                                sap_knowledge.append(r)
                            elif source == 'generated_documentation':
                                doc_parts.append(r)
                            elif source == 'code' or r['metadata'].get('type') in ['form', 'perform', 'select', 'function_call', 'sap_table', 'internal_table', 'class', 'method', 'method_call']:
                                code_parts.append(r)

                        if sap_knowledge:
                            rag_parts.append("## CONNAISSANCES SAP PERTINENTES:")
                            for r in sap_knowledge:
                                name = r['metadata'].get('table', r['metadata'].get('field', 'Inconnu'))
                                type_ = r['metadata'].get('type', 'sap_info')
                                rag_parts.append(f"### {type_}: {name}")
                                rag_parts.append(r['document'])
                                rag_parts.append("---")

                        if doc_parts:
                            rag_parts.append("## EXTRAITS DE DOCUMENTATION PERTINENTS:")
                            for r in doc_parts:
                                name = r['metadata'].get('name', 'Documentation')
                                type_ = r['metadata'].get('type', 'doc')
                                rag_parts.append(f"### {type_}: {name}")
                                rag_parts.append(r['document'])
                                rag_parts.append("---")
                                
                        if code_parts:
                            rag_parts.append("## EXTRAITS DE CODE SOURCE ABAP PERTINENTS:")
                            for r in code_parts:
                                name = r['metadata'].get('name', r['metadata'].get('table', 'Code'))
                                type_ = r['metadata'].get('type', 'code')
                                rag_parts.append(f"### {type_}: {name}")
                                rag_parts.append(f"```abap\n{r['document']}\n```")
                                rag_parts.append("---")

                        rag_context = "\n".join(rag_parts) if rag_parts else ""

                        # Create augmented message with RAG context
                        augmented_messages = st.session_state.messages.copy()
                        if rag_context:
                            augmented_messages.insert(-1, {
                                "role": "system",
                                "content": f"Informations supplémentaires pertinentes pour répondre à la question:\n{rag_context}"
                            })

                    # Get response from LLM
                    with st.chat_message("assistant"):
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        stream = ollama.chat(
                            model=model_name,
                            messages=augmented_messages,
                            stream=True,
                        )
                        for chunk in stream:
                            full_response += chunk["message"]["content"]
                            response_placeholder.markdown(full_response + "▌")

                        response_placeholder.markdown(full_response)

                    st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        # Empty state with helpful info
        st.divider()
        st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; background-color: #FFFFFF; border-radius: 1rem; margin: 2rem 0;'>
            <h2 style='color: #0F4C81; margin-bottom: 1rem;'>👋 Bienvenue !</h2>
            <p style='font-size: 1.1rem; color: #64748B;'>Téléchargez un fichier ABAP pour commencer</p>
            <div style='margin-top: 2rem; color: #94A3B8; font-size: 0.9rem;'>
                <p>Formats supportés : <strong>.abap</strong>, <strong>.txt</strong>, <strong>.pdf</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
