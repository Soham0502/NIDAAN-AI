import google.generativeai as genai
import os
from dotenv import load_dotenv

print("Starting model check...")



# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print(f"API Key loaded: {api_key[:10]}..." if api_key else "❌ No API Key found!")

if not api_key:
    print("\n⚠️ ERROR: GOOGLE_API_KEY not found in .env file")
    print("Make sure your .env file contains:")
    print("GOOGLE_API_KEY=your_actual_api_key_here")
    exit(1)

try:
    # Configure the API
    genai.configure(api_key=api_key)
    print("✓ API configured successfully\n")
    
    print("=" * 70)
    print("FETCHING AVAILABLE MODELS...")
    print("=" * 70)
    
    models_list = list(genai.list_models())
    print(f"\n✓ Found {len(models_list)} total models\n")
    
    vision_models = []
    
    for model in models_list:
        if 'generateContent' in model.supported_generation_methods:
            vision_models.append(model)
            print(f"\n✓ Model Name: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Input Token Limit: {model.input_token_limit}")
            print(f"  Output Token Limit: {model.output_token_limit}")
            print("-" * 70)
    
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: Found {len(vision_models)} models with vision support")
    print("=" * 70)
    
    if vision_models:
        print("\n📋 COPY ONE OF THESE FOR YOUR CODE:")
        for model in vision_models:
            # Extract just the model name without 'models/' prefix
            clean_name = model.name.replace('models/', '')
            print(f'  model_name="{clean_name}"')
    else:
        print("\n⚠️ No models with generateContent found!")
        print("This might be an API key permissions issue.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"\nFull error details: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
print("\n" + "=" * 70)