import requests
import json
from typing import Dict, List, Any


class OllamaDocumentGenerator:
    def __init__(self, model: str = "llama3.1:latest ", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def is_ollama_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama connection error: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model.get("name", "") for model in data.get("models", [])]
        except Exception as e:
            print(f"Error getting models: {e}")
        return []
    
    def generate_documentation(self, 
                               parsed_data: Dict[str, Any], 
                               relevant_elements: List[Dict] = None,
                               raw_code: str = None) -> str:
        context = self._build_context(parsed_data, relevant_elements, raw_code)
        
        # Create strong system prompt + user prompt combined (for /api/generate endpoint)
        system_prompt = system_prompt = """
You are an expert SAP ABAP technical documentation specialist with deep knowledge of SAP architecture, ABAP programming language, and business process logic.

Your task is to analyze ABAP source code and produce clear, complete, and professional technical documentation.

You MUST always structure your documentation in this exact order:

---

## 1. PROGRAM OVERVIEW
- Program/Module name
- General purpose: what business problem this code solves
- High-level summary of what the code does from start to finish
- Entry point and execution flow

---

## 2. TECHNICAL ARCHITECTURE
- List of all components found (functions, classes, forms, includes, reports)
- How they interact with each other
- Execution order and calling hierarchy

---

## 3. DATABASE TABLES USED
For each table found in the code:
- Table name (e.g. KNB1, VBAK, MARA)
- Whether it is a standard SAP table or a custom Z-table
- What data it holds
- How it is used in this code (SELECT, INSERT, UPDATE, DELETE)
- Which function or block accesses it

---

## 4. FUNCTION MODULES / METHODS / FORMS
For each function, method, or form found:

### [FUNCTION NAME]
- **Purpose**: what this function does and why it exists
- **Importing parameters**: each parameter name, type, and what it represents
- **Exporting parameters**: each parameter name, type, and what it returns
- **Changing parameters**: parameters that are both read and modified
- **Tables parameters**: internal tables passed
- **Local variables**: key internal variables and their role
- **Logic walkthrough**: step by step explanation of what the code does
- **Tables accessed**: which DB tables it reads or writes
- **Calls made**: other functions or methods it calls
- **Return behavior**: what it returns and under what conditions
- **Error handling**: how exceptions or errors are handled

---

## 5. DATA FLOW SUMMARY
- How data moves through the program from input to output
- Key transformation points
- Final output or result of the program

---

## 6. BUSINESS LOGIC SUMMARY
- What business process this code implements
- Any business rules encoded in the logic
- Conditions and edge cases handled

---

STRICT RULES:
- Never skip any section even if information is limited — write "Not found in provided code" if needed
- Never hallucinate table names or function names not present in the code
- Use only information from the provided ABAP context
- If a table is a standard SAP table (no Z prefix), briefly explain what it stores in SAP
- If a concept is ABAP-specific (BAPI, FUNCTION MODULE, INCLUDE etc.), explain it simply
- Always use the exact names from the code, never rename or paraphrase identifiers
- Be thorough — incomplete documentation defeats the purpose
"""

        user_prompt = f"""Analyze the following ABAP code and produce complete technical documentation following your instructions exactly.

The code has been pre-parsed into structured JSON blocks. Each block represents a distinct component of the program.

ABAP CODE CONTEXT:
{parsed_data}

DOCUMENTATION REQUIREMENTS:
- Document every single function, form, method, and class found in the context
- Document every single database table accessed anywhere in the code
- Explain the business logic in plain language a non-ABAP developer can understand
- For every parameter, include its technical name, ABAP type, and business meaning
- For every table access, specify whether it is SELECT / INSERT / UPDATE / DELETE
- Connect the dots — explain how the components work together as a complete system

Begin the documentation now. Do not add any preamble or introduction before the documentation structure.
"""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        print(f"Sending request to Ollama model: {self.model}")
        print(f"Prompt length: {len(full_prompt)} characters")
        print(f"API URL: {self.api_url}")
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.3,
                    "num_predict": 1536,
                    "num_ctx": 8192     # Larger context window (8k)
                },
                timeout=300
            )
            
            print(f"Ollama response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Ollama full response: {json.dumps(result, indent=2)[:500]}...")
                return result.get("response", "No response generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure Ollama is running on http://localhost:11434"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Ollama is taking too long to respond. Try using a smaller model or check your Ollama setup."
        except Exception as e:
            return f"Error generating documentation: {str(e)}"
    
    def _build_context(self, parsed_data: Dict[str, Any], 
                      relevant_elements: List[Dict] = None,
                      raw_code: str = None) -> str:
        context_parts = []
        
        if relevant_elements:
            context_parts.append("RELEVANT CODE ELEMENTS:")
            for elem in relevant_elements[:10]:  # Limit to 10 elements max
                meta = elem.get('metadata', {})
                context_parts.append(f"- Type: {meta.get('type', 'unknown')}")
                context_parts.append(f"  Name: {meta.get('name', 'unknown')}")
                context_parts.append("")
        
        context_parts.append("PARSED ABAP DATA:")
        
        # Don't truncate too much - keep more data
        forms = parsed_data.get('forms', [])
        context_parts.append(f"Forms: {', '.join(forms)}")
        
        performs = parsed_data.get('performs', [])
        context_parts.append(f"Performs: {', '.join(performs)}")
        
        function_calls = parsed_data.get('function_calls', [])
        context_parts.append(f"Function Calls: {', '.join(function_calls)}")
        
        sap_tables = parsed_data.get('sap_tables_used', [])
        context_parts.append(f"SAP Tables: {', '.join(sap_tables)}")
        
        internal_tables = parsed_data.get('internal_tables', [])
        context_parts.append(f"Internal Tables: {', '.join(internal_tables)}")
        
        if parsed_data.get('selects'):
            context_parts.append("\nSELECT Statements:")
            for i, select in enumerate(parsed_data['selects'][:5], 1):
                table = select.get('table')
                fields = select.get('fields', [])
                context_parts.append(f"  {i}. Table: {table}, Fields: {', '.join(fields)}")
        
        # Put back CLEANED code (more useful than raw)
        context_parts.append("\nCLEANED ABAP CODE (Full context):")
        # Limit cleaned code to 3000 chars (but keep enough context)
        if raw_code:
            if len(raw_code) > 3000:
                context_parts.append(raw_code[:3000] + "\n... [code truncated]")
            else:
                context_parts.append(raw_code)
        
        return "\n".join(context_parts)
