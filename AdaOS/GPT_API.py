from openai import OpenAI
import json

client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key= "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"
        )
        
response =  client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Please, provide response in JSON. Store answer in dictionary 'answer. In this dictionary must be 2 keys: 'question' and 'response'. Response must be string",
                },
                {
                    "role": "user",
                    "content": "Перечисли 5 видов пива ",
                }
            ],
            model="gpt-4o",
            response_format={ "type" : "json_object"},
            temperature=.3,
            max_tokens=2048,
            top_p=1
        )

print(response.choices[0].message.content)
data = json.loads(response.choices[0].message.content)

response_data = data.get("answer")

question = response_data['question']
answers = response_data["ответ"]

print(question)