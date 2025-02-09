from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_element(self, collection_name, element):
        collection = self.db[collection_name]
        result = collection.insert_one(element)
        return result.inserted_id

    def find_element(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.find_one(query)
        return result

    @staticmethod
    def connect_local(db_name):
        uri = 'mongodb://localhost:27017/'
        return MongoDBManager(uri, db_name)

# Example usage:
# db_manager = MongoDBManager('mongodb://localhost:27017/', 'mydatabase')
# db_manager.insert_element('mycollection', {'name': 'John', 'age': 30})
# print(db_manager.find_element('mycollection', {'name': 'John'}))