import os
import sys

def run_setup():
    print("=" * 60)
    print("              AURA - FIRST-RUN SETUP WIZARD")
    print("=" * 60)
    print("Welcome! AURA is a voice-controlled autonomous assistant.")
    print("This setup wizard will configure your local environment (.env file).")
    print("-" * 60)

    # 1. Prompt for Groq API Key & validate
    print("Step 1: LLM Configuration")
    print("AURA uses the Groq API for intent parsing and vision by default.")
    print("If you do not have an API key, get one for free at: https://console.groq.com/\n")
    
    groq_key = ""
    nlp_model = "llama-3.3-70b-versatile"
    vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    while True:
        groq_key = input("Enter your GROQ_API_KEY: ").strip()
        if not groq_key:
            print("Error: GROQ_API_KEY cannot be empty. Please enter a valid key.")
            continue
        
        print("Validating API key and retrieving available models...")
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            models = [m.id for m in client.models.list().data]
            print("API Key validation successful! Found models:", models)
            
            # Select best NLP model from available list
            if "groq/compound-mini" in models:
                nlp_model = "groq/compound-mini"
            elif "groq/compound" in models:
                nlp_model = "groq/compound"
            elif "llama-3.3-70b-versatile" in models:
                nlp_model = "llama-3.3-70b-versatile"
            elif models:
                # Filter to find any general text models
                text_models = [m for m in models if "whisper" not in m and "prompt-guard" not in m]
                if text_models:
                    nlp_model = text_models[0]
                else:
                    nlp_model = models[0]
            
            # Select best Vision model from available list
            if "meta-llama/llama-4-scout-17b-16e-instruct" in models:
                vision_model = "meta-llama/llama-4-scout-17b-16e-instruct"
            else:
                # Check for other vision models
                vision_candidates = [m for m in models if "vision" in m or "scout" in m]
                if vision_candidates:
                    vision_model = vision_candidates[0]
            
            print(f"Selected NLP Model: {nlp_model}")
            print(f"Selected Vision Model: {vision_model}")
            break
        except Exception as e:
            print(f"Error: Invalid API key or request failed ({e}). Please try again.")

    print("-" * 60)

    # 2. Prompt for Workspace sandboxing directory
    print("Step 2: Security Sandboxing")
    print("AURA runs in safe mode, confining all file operations strictly to a workspace.")
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    default_workspace = os.path.join(project_root, "workspace")
    
    print(f"Default workspace: {default_workspace}")
    workspace_dir = input(f"Enter workspace directory path [Press Enter for default]: ").strip()
    
    if not workspace_dir:
        workspace_dir = default_workspace
    else:
        workspace_dir = os.path.abspath(workspace_dir)

    # Ensure the workspace directory exists
    try:
        os.makedirs(workspace_dir, exist_ok=True)
        print(f"Workspace directory verified/created at: {workspace_dir}")
    except Exception as e:
        print(f"Warning: Could not create workspace directory: {e}")

    print("-" * 60)

    # 3. Create .env file content
    env_content = f"""# AURA Local Configuration
# Generated automatically by setup_wizard.py

# Get your Groq API key from https://console.groq.com/
GROQ_API_KEY={groq_key}

# LLM Configuration (GROQ or OLLAMA)
AURA_LLM_PROVIDER=GROQ

# Model Selections resolved from API key
GROQ_NLP_MODEL={nlp_model}
GROQ_VISION_MODEL={vision_model}

# Ollama Endpoint Configurations (for local offline LLM fallback)
OLLAMA_NLP_URL=http://localhost:11434/api/chat
OLLAMA_NLP_MODEL=llama3.2
OLLAMA_VISION_URL=http://localhost:11434/api/chat
OLLAMA_VISION_MODEL=llava

# Security Sandboxing Configuration
AURA_WORKSPACE_DIR={workspace_dir}
AURA_SAFE_MODE=True
"""

    env_path = os.path.join(project_root, ".env")
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
        print(f"Success! Configuration file created at: {env_path}")
    except Exception as e:
        print(f"Error: Could not write .env file: {e}")
        return False

    print("=" * 60)
    print("AURA configuration complete! Launching services next...")
    print("=" * 60)
    print()
    return True

if __name__ == "__main__":
    run_setup()
