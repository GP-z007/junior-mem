from openai import OpenAI
from mem0 import Memory
from dotenv import load_dotenv

# for future open ai or another models
load_dotenv(".env")

#loading local model
JUNIOR_MODEL_ID = "mlx-community/Qwen3.8-27B-OBLITERATED-OptiQ-4bit"
JUNIOR_BASE_URL = "http://host.docker.internal:8000/v1"
JUNIOR_API_KEY = "SEIG_HEIL"

config = {
    "llm" : {
        "provider": "openai",
        "config":{
            "model": JUNIOR_MODEL_ID,
            "base_url": JUNIOR_BASE_URL,
            "api_key": JUNIOR_API_KEY
        }
    },

    #generating embedder vectors
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1" 
        }
    },
    #storing vectors
    "vector_store": {
        "provider": "qdrant",
        "config":{
            "host": "localhost", "port": 6333
        }
    }
}

#the chat gen to the model
junior_client = OpenAI(
    api_key=JUNIOR_API_KEY,
    base_url=JUNIOR_BASE_URL,
)

m = Memory.from_config(config)

def chat_with_mem(msg: str, user_id: str = "user_1") -> str:
    relevant_mem = m.search(msg, user_id=user_id, limit=3)
    if relevant_mem["results"]:
        memories_str = "\n".join(
            f"- {entry['memory']}" for entry in relevant_mem["results"]
        )
        print(f"Relevant memories found:\n{memories_str}")
    else:
        memories_str = "No previous memories."
        print("No relevant memories found.")

    system_prompt = "You are Junior, a helpful assistant. Use the following memories to inform your response:\n"
    message = [
        {"role": "system", "content": system_prompt + memories_str},
        {"role": "user", "content": msg}
    ]

    response = junior_client.chat.completions.create(
        model=JUNIOR_MODEL_ID,
        messages=message,
        max_tokens=550,
    )
    junior_response = response.choices[0].message.content

    message.append({"role": "assistant", "content": junior_response})

    m.add(message, user_id=user_id, metadata={"session_id": "session_1", "category": "chat_with_mem"})
    
    return junior_response

def main():
    print("Welcome to the Junior Chat with Memory!")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        response = chat_with_mem(user_input)
        print(f"Junior: {response}")

if __name__ == "__main__":
    main()
