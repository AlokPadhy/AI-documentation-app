from groq import Groq

client = Groq(api_key="GROQ_API_KEY")

def generate_document(topic: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional document writer. Generate a well-structured, detailed document on the given topic with sections like Introduction, Key Points, and Conclusion."
            },
            {
                "role": "user",
                "content": f"Generate a comprehensive document about: {topic}"
            }
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    topic = input("Enter a topic to generate a document: ")
    print("\n" + generate_document(topic))
