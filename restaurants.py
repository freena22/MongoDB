

# Making a Connection with MongoClient

from pymongo import MongoClient
import pprint
client = MongoClient('mongodb://localhost:27017')


# Use mongoimport to import the primer-dataset.json already
db = client.test

collection = db.restaurants

one = db.restaurants.find_one()

for item in one:
    print(item)

# OUTPUT: 
'''
 _id
address
borough
cuisine
grades
name
restaurant_id
'''

# checking the cuisine:American 
print(db.restaurants.find({"cuisine":"American"}).count())
# Output: 12366 

print('----------------')

pprint.pprint(collection.find_one())
