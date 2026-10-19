# docs/compile_docs.py
import os
import re

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DOCS_DIR)
OUTPUT_FILE = os.path.join(ROOT_DIR, "AURA_Final_SRS_and_Design_Document.md")

def compile_documents():
    print("[COMPILER] Starting documentation build pipeline...")
    
    # Get all markdown files in the docs directory that start with numbers
    files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".md") and f[:2].isdigit()]
    files.sort()  # Ensure they are processed in order (01, 02, etc.)
    
    compiled_content = []
    
    # Add a global title header block if compiling to a single file
    compiled_content.append("# AURA TECHNICAL SPECIFICATION DOCUMENT\n")
    compiled_content.append("## Software Requirements Specification (SRS) & System Design Document\n")
    compiled_content.append("---\n\n")

    for file_name in files:
        file_path = os.path.join(DOCS_DIR, file_name)
        print(f"[COMPILER] Reading {file_name}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Clean up redundant global title headers inside individual chapters
            content = re.sub(r"^# AURA: TECHNICAL SPECIFICATION.*?\n", "", content, flags=re.IGNORECASE)
            
            compiled_content.append(content)
            compiled_content.append("\n\n---\n\n")  # Section breaks
            
    # Write to final monolithic file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
        out_f.write("".join(compiled_content))
        
    print(f"[COMPILER] Success! Final compiled document written to:\n  {OUTPUT_FILE}")

if __name__ == "__main__":
    compile_documents()
