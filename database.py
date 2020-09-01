from pymongo import MongoClient


# Enchanted col, for new insert and delete functions
# To use it, create obj with db.collection as argument, Example: Ench_col(db.collection)
class Ench_col():
    def __init__(self, collection):
        self.collection = collection

    # parameters: dictionary to insert
    #             list of keys to search (primary key emulation)
    def insert(self, iterator, primary):
        for key in primary:
            if self.collection.find_one({key: iterator[key]}):
                return False
        self.collection.insert(iterator)
        return True

    # parameters: dictionary to delete
    def delete(self, iterator):
        if self.collection.find_one(iterator):
            self.collection.delete_one(iterator)
            return True
        return False


client = MongoClient("mongodb+srv://admin:admin@cluster0.ybdom.mongodb.net/NatashaFlask?retryWrites=true&w=majority")
db = client.NatashaFlask
