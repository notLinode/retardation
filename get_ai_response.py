import openai

def get_response(prompt: str) -> str:
    client = openai.OpenAI(
        api_key="api key",
        base_url="https://chatapi.akash.network/api/v1"
    )

    response = client.chat.completions.create(
        model="Meta-Llama-3-1-405B-Instruct-FP8",
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    #print(response.choices[0].message.content)

    return response.choices[0].message.content