from pymongo import MongoClient, errors
from datetime import datetime, timezone
import time

class ChatDatabase:
    def __init__(self, uri, db_name='chat_database', collection_name='chats', retries=5, delay=5):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.connect_to_mongodb(retries, delay)

    def connect_to_mongodb(self, retries, delay):
        for attempt in range(retries):
            try:
                self.client = MongoClient(self.uri)
                db = self.client[self.db_name]
                self.collection = db[self.collection_name]
                print(f"Connected to MongoDB on attempt {attempt + 1}")
                return
            except errors.ServerSelectionTimeoutError as err:
                print(f"Attempt {attempt + 1} of {retries} failed: {err}")
                time.sleep(delay)
        raise ConnectionError(f"Failed to connect to MongoDB after {retries} attempts")

    def format_chat(self, user_id, questions_answers):
        formatted_chat = {
            "user_id": user_id,
            "chats": []
        }
        chat_id = f"chat_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        current_timestamp = datetime.now(timezone.utc).isoformat()
        chat = {
            "chat_id": chat_id,
            "timestamp": current_timestamp,
            "messages": []
        }
        for qa in questions_answers:
            question_message = {
                "sender": "human_user",
                "timestamp": current_timestamp,
                "message": qa["question"]
            }
            answer_message = {
                "sender": "ai_chatbot",
                "timestamp": current_timestamp,
                "message": qa["answer"]
            }
            chat["messages"].append(question_message)
            chat["messages"].append(answer_message)
        formatted_chat["chats"].append(chat)
        return formatted_chat

    def insert_chat(self, user_id, questions_answers):
        formatted_chat_data = self.format_chat(user_id, questions_answers)
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$push": {"chats": {"$each": formatted_chat_data["chats"]}}},
                upsert=True
            )
        except errors.PyMongoError as e:
            print(f"Error inserting data into MongoDB: {e}")

    def get_chat_history(self, user_id):
        try:
            chat_data = self.collection.find_one({"user_id": user_id})
            if not chat_data or 'chats' not in chat_data:
                return "No chat history found."
            else:
                chat_history = ""
                for chat in chat_data['chats']:
                    for message in chat['messages']:
                        chat_history += f"{message['sender']}: {message['message']}\n"
                return chat_history
        except errors.PyMongoError as e:
            return f"Error retrieving chat data: {e}"
