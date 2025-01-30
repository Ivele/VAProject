import requests
import datetime as dt
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pymorphy2
import os
from openai import OpenAI
import json

class ActionAskGPT(Action):
    def name(self) -> str:
        return "action_ask_GPT"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):

        ask = tracker.get_slot("search_query")

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
                    "content": ask,
                }
            ],
            model="gpt-4o",
            response_format={ "type" : "json_object"},
            temperature=.3,
            max_tokens=2048,
            top_p=1
        )

        data = json.loads(response.choices[0].message.content)

        response_data = data.get("answer")

        question = response_data['question']
        answer = response_data["response"]

        dispatcher.utter_message(text= f"Ответ: {answer}")

        return[SlotSet("search_query")]
    

class АctionSaveExampleToIntent(Action):
    def name(self) -> str:
        return "action_save_example_to_intent"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):

        directory = "data/data_nlu"
        intent_name = tracker.latest_message['intent'].get('name')
        new_example = tracker.latest_message.get("text")

        last_entity_value = tracker.get_slot("last_entity_value")
        last_entity_name = tracker.get_slot("last_entity_name")
        filepath = os.path.join(directory, f"{intent_name}.yml")
        
        if last_entity_name == "":
            message = new_example
        else:
            message = new_example.replace(last_entity_value, f"[{last_entity_value}]({last_entity_name})")

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        if not os.path.exists(filepath):
            dispatcher.utter_message(text=f"Файл для интента {intent_name} не найден в {directory}")
            return
        
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        if message in content:
            return
        
        with open(filepath, "a", encoding="utf-8") as file:
            file.write(f"\n    - {message}")
        
        SlotSet("last_entity_name", "")
        
class ActionShowTime(Action):
    def name(self) -> str:
        return "action_show_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):

        current_time = dt.datetime.now().strftime('%H:%M:%S')

        dispatcher.utter_message(text=f"Текущее время: {current_time}")
        SlotSet("last_entity_name", "")

        return []
    
class ActionGetWeather(Action):
    def name(self) -> str:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):

        user_location = tracker.get_slot("last_entity_value")

        morph = pymorphy2.MorphAnalyzer()
        word = user_location
        lemma = morph.parse(word)[0].normal_form
        lemma = lemma.capitalize()

        api_key = "c5d07661c7168c73f4c654904566fbc4"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={lemma}&appid={api_key}&units=metric&lang=ru"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            dispatcher.utter_message(text=f"В городе {lemma} сейчас {temp}°C, {description}.")
        else:
            dispatcher.utter_message(text="Я не смог найти погоду для этого города. Попробуйте другой город.")
            SlotSet("last_entity_name", "")
            return []

