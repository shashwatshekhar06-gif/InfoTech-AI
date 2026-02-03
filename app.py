import requests

prompt = """ Explain how india won the finals of 2011 ODI world cup against Sri Lanka led by MS Dhoni """
try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "hf.co/unsloth/Qwen3-4B-GGUF:latest",
            "prompt": prompt,
            "stream": False,
            "options":{
                "num_predict": 200
            }
        },
        timeout=120
    )

    print("AI Response:\n")
    print(response.json()["response"])

except Exception as e:
    print("Error:", e)
