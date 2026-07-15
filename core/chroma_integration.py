import chromadb
import re
from chromadb.config import Settings
from typing import Dict, List, Any
import json


class ChromaABAPManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create collection for both ABAP code and SAP knowledge base
        self.collection = self.client.get_or_create_collection(
            name="abap_and_sap_knowledge",
            metadata={"description": "ABAP code elements + SAP knowledge base for documentation generation"}
        )
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata to ensure all values are valid ChromaDB types (str, int, float, bool)."""
        sanitized = {}
        for key, value in metadata.items():
            if value is None:
                sanitized[key] = ""  # Replace None with empty string
            elif isinstance(value, (list, dict)):
                sanitized[key] = json.dumps(value)  # Convert complex types to JSON string
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value  # Keep valid types as-is
            else:
                sanitized[key] = str(value)  # Convert everything else to string
        return sanitized
    
    def index_parsed_data(self, parsed_data: Dict[str, Any], raw_code: str = None) -> int:
        documents = []
        metadatas = []
        ids = []
        idx = 0
        
        for form_name in parsed_data.get("forms", []):
            doc_content = f"FORM: {form_name}"
            if raw_code:
                form_code = self._extract_form_code(raw_code, form_name)
                if form_code:
                    doc_content = form_code
            
            documents.append(doc_content)
            metadatas.append(self._sanitize_metadata({
                "type": "form",
                "name": form_name,
                "element_id": f"form_{idx}",
                "source": "code"
            }))
            ids.append(f"form_{idx}")
            idx += 1
        
        for perform_name in parsed_data.get("performs", []):
            documents.append(f"PERFORM: {perform_name}")
            metadatas.append(self._sanitize_metadata({
                "type": "perform",
                "name": perform_name,
                "element_id": f"perform_{idx}",
                "source": "code"
            }))
            ids.append(f"perform_{idx}")
            idx += 1
        
        for select_stmt in parsed_data.get("selects", []):
            table = select_stmt.get("table", "UNKNOWN")
            fields = ", ".join(select_stmt.get("fields", []))
            doc_content = f"SELECT from {table} fields: {fields}"
            if raw_code:
                select_code = self._extract_select_code(raw_code, table)
                if select_code:
                    doc_content = select_code
            
            documents.append(doc_content)
            metadatas.append(self._sanitize_metadata({
                "type": "select",
                "table": table,
                "fields": json.dumps(select_stmt.get("fields", [])),
                "element_id": f"select_{idx}",
                "source": "code"
            }))
            ids.append(f"select_{idx}")
            idx += 1
        
        for func_call in parsed_data.get("function_calls", []):
            documents.append(f"CALL FUNCTION: {func_call}")
            metadatas.append(self._sanitize_metadata({
                "type": "function_call",
                "name": func_call,
                "element_id": f"func_{idx}",
                "source": "code"
            }))
            ids.append(f"func_{idx}")
            idx += 1
        
        for table_name in parsed_data.get("sap_tables_used", []):
            documents.append(f"SAP TABLE: {table_name}")
            metadatas.append(self._sanitize_metadata({
                "type": "sap_table",
                "name": table_name,
                "element_id": f"saptable_{idx}",
                "source": "code"
            }))
            ids.append(f"saptable_{idx}")
            idx += 1
        
        for internal_table in parsed_data.get("internal_tables", []):
            documents.append(f"INTERNAL TABLE: {internal_table}")
            metadatas.append(self._sanitize_metadata({
                "type": "internal_table",
                "name": internal_table,
                "element_id": f"inttable_{idx}",
                "source": "code"
            }))
            ids.append(f"inttable_{idx}")
            idx += 1
            
        for class_name in parsed_data.get("classes", []):
            doc_content = f"CLASS: {class_name}"
            if raw_code:
                class_code = self._extract_class_code(raw_code, class_name)
                if class_code:
                    doc_content = class_code
            documents.append(doc_content)
            metadatas.append(self._sanitize_metadata({
                "type": "class",
                "name": class_name,
                "element_id": f"class_{idx}",
                "source": "code"
            }))
            ids.append(f"class_{idx}")
            idx += 1

        for method_name in parsed_data.get("methods", []):
            doc_content = f"METHOD: {method_name}"
            if raw_code:
                method_code = self._extract_method_code(raw_code, method_name)
                if method_code:
                    doc_content = method_code
            documents.append(doc_content)
            metadatas.append(self._sanitize_metadata({
                "type": "method",
                "name": method_name,
                "element_id": f"method_{idx}",
                "source": "code"
            }))
            ids.append(f"method_{idx}")
            idx += 1

        for method_call in parsed_data.get("method_calls", []):
            documents.append(f"METHOD CALL: {method_call}")
            metadatas.append(self._sanitize_metadata({
                "type": "method_call",
                "name": method_call,
                "element_id": f"methodcall_{idx}",
                "source": "code"
            }))
            ids.append(f"methodcall_{idx}")
            idx += 1
        
        for handler_reg in parsed_data.get("set_handler_registrations", []):
            documents.append(f"SET HANDLER: {handler_reg}")
            metadatas.append(self._sanitize_metadata({
                "type": "set_handler_registration",
                "name": handler_reg,
                "element_id": f"sethandler_{idx}",
                "source": "code"
            }))
            ids.append(f"sethandler_{idx}")
            idx += 1
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        return len(documents)
    
    def _extract_form_code(self, raw_code: str, form_name: str) -> str:
        pattern = rf"\bFORM\s+{form_name}\b.*?\bENDFORM\b"
        match = re.search(pattern, raw_code, flags=re.IGNORECASE | re.DOTALL)
        return match.group(0) if match else None

    def _extract_class_code(self, raw_code: str, class_name: str) -> str:
        pattern = rf"\bCLASS\s+{re.escape(class_name)}\b.*?\bENDCLASS\b"
        matches = re.findall(pattern, raw_code, flags=re.IGNORECASE | re.DOTALL)
        return "\n\n".join(matches) if matches else None

    def _extract_method_code(self, raw_code: str, method_name: str) -> str:
        pattern = rf"\bMETHOD\s+{re.escape(method_name)}\b.*?\bENDMETHOD\b"
        match = re.search(pattern, raw_code, flags=re.IGNORECASE | re.DOTALL)
        return match.group(0) if match else None
    
    def _extract_select_code(self, raw_code: str, table_name: str) -> str:
        pattern = rf"\bSELECT\b.*?\bFROM\s+{table_name}\b.*?\."
        match = re.search(pattern, raw_code, flags=re.IGNORECASE | re.DOTALL)
        return match.group(0) if match else None
    
    def query_relevant_elements(self, query_text: str, n_results: int = 10) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        relevant_elements = []
        # Check if we have any results
        if results and results.get('ids') and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                # Make sure all required fields exist
                doc = results['documents'][0][i] if results.get('documents') and len(results['documents'][0]) > i else ""
                meta = results['metadatas'][0][i] if results.get('metadatas') and len(results['metadatas'][0]) > i else {}
                dist = results['distances'][0][i] if results.get('distances') and len(results['distances'][0]) > i else None
                
                relevant_elements.append({
                    'id': results['ids'][0][i],
                    'document': doc,
                    'metadata': meta,
                    'distance': dist
                })
        
        return relevant_elements
    
    def get_all_elements(self) -> List[Dict]:
        results = self.collection.get()
        elements = []
        for i in range(len(results['ids'])):
            elements.append({
                'id': results['ids'][i],
                'document': results['documents'][i],
                'metadata': results['metadatas'][i]
            })
        return elements
    
    def index_sap_knowledge_base(self, knowledge_base_path: str = None) -> int:
        """Index SAP knowledge base from JSON file into ChromaDB"""
        try:
            if knowledge_base_path is None:
                # Default to the sap_knowledge_base.json in the same directory as this file
                import os
                knowledge_base_path = os.path.join(os.path.dirname(__file__), "../sap_knowledge_base.json")
                knowledge_base_path = os.path.abspath(knowledge_base_path)
            
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge_base = json.load(f)
            # Handle case where file is wrapped in a list
            if isinstance(knowledge_base, list) and len(knowledge_base) > 0:
                knowledge_base = knowledge_base[0]
        except FileNotFoundError:
            print(f"Warning: SAP knowledge base not found at {knowledge_base_path}")
            return 0
        except Exception as e:
            print(f"Error loading SAP knowledge base: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
        
        documents = []
        metadatas = []
        ids = []
        idx = 0
        
        # Add SAP tables
        for table_name, table_data in knowledge_base.get('tables', {}).items():
            # Create a rich text document for each table
            doc_parts = [f"SAP Table: {table_name}"]
            if 'purpose' in table_data:
                doc_parts.append(f"Purpose: {table_data['purpose']}")
            if 'description' in table_data:
                doc_parts.append(f"Description: {table_data['description']}")
            if 'key_fields' in table_data:
                doc_parts.append(f"Key Fields: {', '.join(table_data['key_fields'])}")
            if 'related_tables' in table_data:
                doc_parts.append(f"Related Tables: {', '.join(table_data['related_tables'])}")
            
            doc_parts.append("\nFields:")
            for field_name, field_data in table_data.get('fields', {}).items():
                field_parts = [f"- {field_name}:"]
                if 'description' in field_data:
                    field_parts.append(f"  Description: {field_data['description']}")
                if 'data_element' in field_data:
                    field_parts.append(f"  Data Element: {field_data['data_element']}")
                if 'domain' in field_data:
                    field_parts.append(f"  Domain: {field_data['domain']}")
                if 'purpose' in field_data:
                    field_parts.append(f"  Purpose: {field_data['purpose']}")
                if 'category' in field_data:
                    field_parts.append(f"  Category: {field_data['category']}")
                doc_parts.append("\n".join(field_parts))
            
            if 'wrong_descriptions' in table_data:
                doc_parts.append(f"\nNOT TO CONFUSE WITH: {', '.join(table_data['wrong_descriptions'])}")
            
            if 'in_this_program' in table_data:
                doc_parts.append(f"\nIn this program: {table_data['in_this_program']}")
            
            doc = "\n".join(doc_parts)
            documents.append(doc)
            metadatas.append(self._sanitize_metadata({
                "source": "sap_knowledge_base",
                "type": "sap_table_definition",
                "table": table_name,
                "category": "table_purpose"
            }))
            ids.append(f"sap_table_{idx}")
            idx += 1
        
        # Add field index entries
        for field_name, field_data in knowledge_base.get('field_index', {}).items():
            doc_parts = [
                f"SAP Field: {field_name}",
                f"Found in tables: {', '.join(field_data.get('tables', []))}"
            ]
            if 'category' in field_data:
                doc_parts.append(f"Category: {field_data['category']}")
            doc = "\n".join(doc_parts)
            documents.append(doc)
            metadatas.append(self._sanitize_metadata({
                "source": "sap_knowledge_base",
                "type": "sap_field_index",
                "field": field_name,
                "category": "field_index"
            }))
            ids.append(f"sap_field_{idx}")
            idx += 1
        
        # Add wrong descriptions (error prevention)
        for field, wrong_descs in knowledge_base.get('wrong_descriptions', {}).items():
            doc_parts = [f"CRITICAL: {field} is NOT:"]
            for desc in wrong_descs:
                doc_parts.append(f"  - {desc}")
            doc = "\n".join(doc_parts)
            documents.append(doc)
            metadatas.append(self._sanitize_metadata({
                "source": "sap_knowledge_base",
                "type": "sap_error_prevention",
                "field": field,
                "category": "error_prevention"
            }))
            ids.append(f"sap_wrong_{idx}")
            idx += 1
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        return len(documents)
    
    def clear_collection(self):
        self.client.delete_collection("abap_and_sap_knowledge")
        self.collection = self.client.create_collection(
            name="abap_and_sap_knowledge",
            metadata={"description": "ABAP code elements + SAP knowledge base for documentation generation"}
        )
    
    def reset_session_data(self):
        """Remove previously indexed code and generated documentation, keeping SAP knowledge base."""
        try:
            self.collection.delete(where={"source": {"$in": ["code", "generated_documentation"]}})
        except Exception as e:
            print(f"Error resetting session data: {e}")
            
    def is_sap_kb_indexed(self) -> bool:
        """Check if the SAP knowledge base is already indexed in the collection."""
        try:
            results = self.collection.get(where={"source": "sap_knowledge_base"}, limit=1)
            return len(results.get("ids", [])) > 0
        except Exception:
            return False
    
    def index_generated_documentation(self, program_doc, form_docs):
        """Index the generated documentation into ChromaDB"""
        documents = []
        metadatas = []
        ids = []
        idx = 0
        
        # Index program-level documentation
        if program_doc:
            documents.append(program_doc)
            metadatas.append(self._sanitize_metadata({
                "source": "generated_documentation",
                "type": "program_doc",
                "name": "Program Documentation"
            }))
            ids.append(f"doc_program_{idx}")
            idx += 1
        
        # Index each form's documentation
        for form_name, form_doc in form_docs.items():
            documents.append(form_doc)
            metadatas.append(self._sanitize_metadata({
                "source": "generated_documentation",
                "type": "form_doc",
                "name": f"FORM: {form_name}"
            }))
            ids.append(f"doc_form_{idx}")
            idx += 1
        
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        return len(documents)
