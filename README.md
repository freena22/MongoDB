# MongoDB Basic Tutorial

Key Terms:
  - Document: a record in MongoDB with JSON format, similar to 'row' in SQL
  - Collection: similar to 'table' in SQL, but not require the same schema
  - Field: similar to 'column' in SQL
  - A unique '-id' field acts as a primary key
  
Why Mongo DB?

-	Flexible Schema (Multiple Schemas)
-	Flexible Deployment
-	Designed for Big data (distributed system)
-	Aggregation Framework

### MongoDB Shell (mongo)

Import JSON Dataset:
  - run a mongod 
```sh
$ mongoimport -d databasename -c collectionname --file stocks.json
```
Use Mongo Shell:
```sh
$ ./mongo
> show dbs    # show the databases
> show collections  # show the collection names under current database
> use test    # swithced to db test
> db.createCollection('test1')  # return {'ok':1} 
> db.test1.drop()   # delete the collection - test1
> db.dropDatabase()  # use current database first then delete it
```

### Insert Data 

Use insert() method to add documents to a collection. If you attempt to add documents to a collection that does not exist, MongoDB will create the collection for you.
```sh
$ > use test
$ > db.createCollection('test2')
$ > db.test2.insert(
   {
    "address" : {
         "street" : "2 Avenue",
         "zipcode" : "10075",
         "building" : "1480",
         "coord" : [ -73.9557413, 40.7720266 ]
      },
      "borough" : "Manhattan",
      "cuisine" : "Italian",
      "name" : "Vella",
      "restaurant_id" : "41704620"
   }
)
# Return WriteResult({ "nInserted" : 1 }), if success
```
OR in Pymongo, create a dict then insert the dict 
```
>> dict = {}
>> db.test2.insert(dict)
```

### Find or Query Data
Sytax: db.collection.find(query,projection)

```sh
$ db.test2.find().pretty()   # find all documents
$ db.test2.find({'cuisine':'Italian'}).pretty()  # find specify conditions
# find by a field in an embedded document
$ db.test2.find({'address.zipcode':'10075'} 
$ db.test2.findOne()  # find one document
```

Specify Conditions with Operators -- {<field1>:{<operator1>:<value1>}}

```sh
$ db.test2.find({'address.building':{'$gt':200}}  # greataer than $gt
$ db.test2.find({address.zipcode':{'$lt':22022}}  # less than $lt
# Others: $gte/$lte/$ne
```
Combine Conditions:
```sh
$ db.test2.find({'cuisine':'Italian','address.zipcode':'12222'}) # logic AND
$ db.test2.find(
     {$or: [{'cuisine':'Italian','address.zipcode':'12222'}]}
     )      # Logic OR
$ db.test2.find().sort({'cuisine': 1 ,'address.zipcode': 1})
# sorted first by the cuisine field in ascending order, then by the zipcode
```
Projection Parameter:
```sh
$ db.test2.find({'cuisine':'Italian'},{"name": 1, restaurant_id": 1, '_id: 0}
# only show 'name' and 'restaurant_id' 
```

### Update Data
```sh
$ db.test2.update({"cuisine" : "Italian"},{$set:{'name':'luka'}}).pretty()
# update defined docuemnt with second parameter
```
By default, the update() method updates a single document. To update multiple documents, use the 'multi:True' ...
```sh
$ db.test2.update(
     {'address.zipcode':'10012'},
     {$set:{'cuisine':'not decided'}},
     {multi : true}  # update all matched
 )
```
### Remove Data
```sh
# Remove All documents that match a condition
$ db.test1.remove({'name':'luka'})
# Limit the remove operation to only one of the matching documents
$ db.test1.remove({'name':''luka'},{justOne: true})
# Remove all documents from a collection -- empty dict
$ db.test1.remove({})   
```
### Others functions


1. $exists:0 -- fields with no values in them
```sh
$ db.test1.find({'name':'luka'},{'$exists': 0}}).count()
$ db.test1.find(
     {'population': {'$gt':25000}},
     {'$exists':1}
  )     # find the operation with values 
```
2. regular expression -- $regex
```sh
$ db.test1.find({'name': {'%regex':'[Ll]uka'}})
```
3. in and all 
```sh
$ db.autos.find({'modelyears':{'$in':[1966,1967,1968]}})
$ db.autos.find({'modelyears':{'$all':[1966,1967,1968]}})
```
4. limit() & skip()
```sh
# Output limit numbers of documents
$ db.test1.find({'name':'luka'}).limit(2)
# skip the first documents
$ db.test1.find({'name':'luka'}).skip(5)
```
### Data Aggregation
#####  1. Aggregation Pipeline:

The MongoDB aggregation pipeline consists of stages. Each stage transforms the documents as they pass through the pipeline. 
##### Stages: $match -- $group -- $sort -- $project

1. $match: Use the $match stage to filter documents.
2. $group: Use the $group to group by a specified key, specify the group by key in the _id field. 
```sh
db.restaurants.aggregate(
   [
     { $match: { "borough": "Queens", "cuisine": "Brazilian" } },
     { $group: { "_id": "$address.zipcode" , "count": { $sum: 1 } } }
   ]
)   # $match as the filter to select certian documents then $group 
# Output:
{ "_id" : "11368", "count" : 1 }
{ "_id" : "11106", "count" : 3 }
{ "_id" : "11377", "count" : 1 }
{ "_id" : "11103", "count" : 1 }
{ "_id" : "11101", "count" : 2 }
```
```sh
% db.movie.aggregate([{$group:{'_id':'$directed_by'}}])
# Output: {'_id': 'David Fincher'}
          {'_id': 'Robert Zemeckis'}
          
$ db.movie.aggregate([{$group:{'_id': '$directed_by', 'num_movie':{$sum:1}}}])
# Output: {'_id': 'David Fincher', 'num_movie': 2 }
          {'_id': 'Robert Zemeckis', 'num_movie': 1 }
** $avg:
$ db.movie.aggregate([{$group:{'_id': '$directed_by', 'num_movie':{$avg:$likes}}}])
```
3. $sort: 1 for ascending/-1 for decendenting 
```sh
$ db.tweets.aggregate([
     {'$group': {'_id':'$user.screen_name', 'count':{'$sum':1}}},
     {'$sort': {'count': -1}}])  # decendenting order
```
4. $project: create the output structure
```sh
# Question: Who has the highest followers to friends ratio?
db.tweets.aggregate([
    {'$match': { 'user.friends_count': { '$gt': 0},
                 'user.followers_count':{'$gt':0}}},
    {'$project': {'ratio': {'$divide': ['$user.followers_count', 
                                        'user.friends_count']},
                            'sreen_name': '$user.screen_name'}},
    {'$sort': { 'ratio': -1 }},
    {'$limit': 1 }]
)
```
#####  2. Other Aggregation Functions:

(1) $unwind -- duplicates each document in the pipeline, once per array element

```sh
{
        "_id" : 1,
        "shirt" : "Half Sleeve",
        "sizes" : [
                "medium",
                "XL",
                "free"
        ]
}

$ db.test1.aggregate( [ {'$unwind': '$size'} ] )
Output:
{ "_id" : 1, "shirt" : "Half Sleeve", "sizes" : "medium" }
{ "_id" : 1, "shirt" : "Half Sleeve", "sizes" : "XL" }
{ "_id" : 1, "shirt" : "Half Sleeve", "sizes" : "free" }

# Question: who included the most user mentions in their tweets?
$ db.tweets.aggregate([
  {'$unwind':'$entities.user_mentions'},
  {'$group': { '_id': '$user.screen_name',
               'count': {'$sum': 1 }}},
  {'$sort': { 'count' : -1 }},
  {'$limit': 1 } ] )
```
(2) $push: appends a specified value to an array.
If the mentioned field is absent in the document to update, the $push operator add it as a new field and includes mentioned value as its element. If the updating field is not an array type field the operation failed.
```sh
# Append a Value to an Array
$ db.students.update(
   { _id: 1 },
   { $push: { scores: 89 } }
)
# Append Multiple Values to an Array
$ db.students.update(
   { name: "joe" },
   { $push: { scores: { $each: [ 90, 92, 85 ] } } }
)
```
(3) $addToSet: adds a value to an array unless the value is already present, in which case $addToSet does nothing to that array.
```sh
{ _id: 2, item: "cable", tags: [ "electronics", "supplies" ] }
$ db.inventory.update(
   { _id: 2 },
   { $addToSet: { tags: { $each: [ "camera", "electronics", "accessories" ] } } })
# Output:
{
  _id: 2,
  item: "cable",
  tags: [ "electronics", "supplies", "camera", "accessories" ]
}
```
### Indexes
Indexes can support the efficient execution of queries. Without indexes, MongoDB must perform a collection scan (scan every document in a collection). If an appropriate index exists for a query, MongoDB use the index (B tree) to limit the search times.
- createIndex(), specify 1 for ascending index type, -1 for descending index
- createIndex() only creates an index if the index does not exist.
```sh
$ db.restaurants.createIndex({'cuisine': 1})
# Output:
{
	"createdCollectionAutomatically" : false,
	"numIndexesBefore" : 1,
	"numIndexesAfter" : 2,
	"ok" : 1
}
# Create a compound index

$ db.restaurants.createIndex({'cuisine': 1, 'address.zipcode': -1 })
# Output:
{
	"createdCollectionAutomatically" : false,
	"numIndexesBefore" : 2,
	"numIndexesAfter" : 3,
	"ok" : 1
}
```
- Geospatial indexes
step1: location [x,y]
step2: createindex ( { 'location': ...})
step3: $near
```sh
$ db.nodes.find( { 'loc': { '$near': [41.94, -87.65]}, 'tg': {'$exists': 1 })
```
### Atomic Operation
If a document has hundred fields the update statement will either update all the fields or none, hence maintaining atomicity at the document-level.
```sh
# Consider the following products document −
{
   "_id":1,
   "product_name": "Samsung S3",
   "category": "mobiles",
   "product_total": 5,
   "product_available": 3,
   "product_bought_by": [
      {
         "customer": "john",
         "date": "7-Jan-2014"
      },
      {
         "customer": "mark",
         "date": "8-Jan-2014"
      }
   ]
}
# findAndModify() method to searches and updates the document in the same go
$ >db.products.findAndModify({ 
   query:{_id:2,product_available:{$gt:0}}, 
   update:{ 
      $inc:{product_available:-1}, 
      $push:{product_bought_by:{customer:"rob",date:"9-Jan-2014"}} 
   }})
# whenever a new customer buys the product, it will first check if the product is still available using 'product_available' field. If available, we will reduce the value of product_available field as well as insert the new customer's embedded document in the 'product_bought_by' field.
```
#### Common Atomic Operation commands
```sh
$set: {$set : { field : value}} -- 'to set a value for updating'
$unset: {$unset : { field : 1}} -- 'to delete a value'
$inc: {$inc: { filed : value}} -- 'increments a field by a specified value'
($ db.movie.update({title:'Seven'},{$set:{likes:2}}) # add 2 more liles 
$push: {$push: { field: value}} -- 'appends a specified value to an array'
$pushAll: {$pushAll: { field: value_array}} -- 'append multiple values to an array'
$rename: { old_field_name : new_field_name }} -- 'rename the field name'
```


#### Reference

1. [Getting Started with MongoDB (MongoDB Shell Edition)](https://docs.mongodb.com/getting-started/shell/)
2. [w3resource-MongoDB Tutorial](http://www.w3resource.com/mongodb/introduction-mongodb.php)
3.  [Udacity --Data Wrangling with MongoDB](https://www.udacity.com/course/data-wrangling-with-mongodb--ud032)
4. (https://github.com/StevenSLXie/Tutorials-for-Web-Developers/blob/master/MongoDB%20极简实践入门.md)
