import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from mem0 import Memory


JUNIOR_MODEL_ID = "mlx-community/Qwen3.8-27B-OBLITERATED-OptiQ-4bit"
JUNIOR_BASE_URL = "http://host.docker.internal:8000/v1"
JUNIOR_API_KEY = "SEIG_HEIL"


config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": JUNIOR_MODEL_ID,
            "openai_base_url": JUNIOR_BASE_URL,
            "api_key": JUNIOR_API_KEY,
        }
    },

    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1",
            "embedding_dims": 384,
        }
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "junior_memories",
            "embedding_model_dims": 384,
        }
    },
}


openai_client = OpenAI(
    api_key=JUNIOR_API_KEY,
    base_url=JUNIOR_BASE_URL,
)

memory = Memory.from_config(config)


def index(request):
    return render(request, "chat/index.html")


@csrf_exempt
def api_chat(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        user_message = data.get("message", "").strip()
        user_id = data.get("user_id", "user_1")

        if not user_message:
            return JsonResponse(
                {"error": "Empty message"},
                status=400
            )

        # 1. Retrieve relevant memories
        search_res = memory.search(
            user_message,
            filters={"user_id": user_id},
            limit=3
        )

        recalled_memories = [
            m["memory"]
            for m in search_res.get("results", [])
            if m.get("memory")
        ]

        if recalled_memories:
            memories_str = "\n".join(
                f"- {m}" for m in recalled_memories
            )
        else:
            memories_str = "No prior memories."

        # 2. Build prompt
        system_prompt = (
            "You are Junior, a helpful assistant. "
            "Use these relevant memories if useful:\n"
            f"{memories_str}"
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        # 3. Generate response
        response = openai_client.chat.completions.create(
            model=JUNIOR_MODEL_ID,
            messages=messages,
            max_tokens=550,
        )

        assistant_response = (
            response.choices[0].message.content or ""
        ).strip()

        # 4. Store conversation in long-term memory
        memory_messages = [
            {
                "role": "user",
                "content": user_message
            },
            {
                "role": "assistant",
                "content": assistant_response
            }
        ]

        memory.add(
            memory_messages,
            user_id=user_id,
            metadata={
                "category": "web_chat"
            }
        )

        return JsonResponse({
            "response": assistant_response,
            "recalled_memories": recalled_memories
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    except Exception as e:
        print("Junior error:", e)

        return JsonResponse(
            {"error": str(e)},
            status=500
        )