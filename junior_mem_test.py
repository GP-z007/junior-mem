from mem0 import Memory
from dotenv import load_dotenv

load_dotenv()
m = Memory()

# the msg sequence for testing the memory
message = [
    {
        "role": "user",
        "content": "I'm planning to watch a movie tonight. Any recommendations?",
    },
    {
        "role": "junior",
        "content": "How about a thriller movies? They can be quite engaging.",
    },
    {
        "role": "user",
        "content": "I'm not a big fan of thriller movies but I love sci-fi movies.",
    },
    {
        "role": "junior",
        "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future.",
    },
]

# store the messages in memory

result = m.add(message,user_id="user_1",meta_data={"session_id": "session_1",
                                                   "category": "movie_recommendation"})

#get all the memory for the user
all_memories = m.get_all(user_id="user_1")

# search for the related memories

related_memories = m.search("Describe me.", user_id="user_1")

print("Junior: ", related_memories)
