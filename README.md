# MongoDB Basic Tutorials 

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

Import Json Dataset:
  - run a mongod 
```
$ mongoimport -d databasename -c collectionname --file stocks.json
```
Use Mongo Shell:
```
$ ./mongo
> show dbs    # show the databases
> show collections  # show the collection names under current database
> use test    # swithced to db test
> db.createCollection('test1')  # return {'ok':1} 
> db.test1.drop()   # delete the collection - test1
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

```
$ db.test2.find().pretty()   # find all documents
$ db.test2.find({'cuisine':'Italian'}).pretty()  # find specify conditions
# find by a field in an embedded document
$ db.test2.find({'address.zipcode':'10075'} 
$ db.test2.findOne()  # find one document
```

Specify Conditions with Operators -- {<field1>:{<operator1>:<value1>}}

```
$ db.test2.find({'address.building':{'$gt':200}}  # greataer than $gt
$ db.test2.find({address.zipcode':{'$lt':22022}}  # less than $lt
# Others: $gte/$lte/$ne
```
Combine Conditions:
```
$ db.test2.find({'cuisine':'Italian','address.zipcode':'12222'}) # logic AND
$ db.test2.find(
     {$or: [{'cuisine':'Italian','address.zipcode':'12222'}]}
     )      # Logic OR
$ db.test2.find().sort({'cuisine': 1 ,'address.zipcode': 1})
# sorted first by the cuisine field in ascending order, then by the zipcode
```
Projection Parameter:
```
$ db.test2.find({'cuisine':'Italian'},{"name": 1, restaurant_id": 1, '_id: 0}
# only show 'name' and 'restaurant_id' 
```

### Update Data
```
$ db.test2.update({"cuisine" : "Italian"},{$set:{'name':'luka'}}).pretty()
# update defined docuemnt with second parameter
```
By default, the update() method updates a single document. To update multiple documents, use the 'multi:True' ...
```
$ db.test2.update(
     {'address.zipcode':'10012'},
     {$set:{'cuisine':'not decided'}},
     {multi : true}
 )
```
### Remove Data
```
# Remove All documents that match a condition
$ db.test1.remove({'name':'luka'})
# Limit the remove operation to only one of the matching documents
$ db.test1.remove({'name':''luka'},{justOne: true})
# Remove all documents from a collection -- empty dict
$ db.test1.remove({})   
```
### Others functions


1. $exists:0 -- fields with no values in them
```
$ db.test1.find({'name':'luka'},{'$exists': 0}}).count()
$ db.test1.find(
     {'population': {'$gt':25000}},
     {'$exists':1}
  )     # find the operation with values 
```
2. regular expression -- $regex
```
$ db.test1.find({'name': {'%regex':'[Ll]uka'}})
```
3. in and all 
```
$ db.autos.find({'modelyears':{'$in':[1966,1967,1968]}})
$ db.autos.find({'modelyears':{'$all':[1966,1967,1968]}})
```
### Data Aggregation

Similar to the GROUP BY in SQL
1. $group: Use the $group to group by a specified key, specify the group by key in the _id field. 
```
% db.movie.aggregate([{$group:{'_id':'$directed_by'}}])
# Output: {'_id': 'David Fincher'}
          {'_id': 'Robert Zemeckis'}
          
$ db.movie.aggregate([{$group:{'_id': '$directed_by', 'num_movie':{$sum:1}}}])
# Output: {'_id': 'David Fincher', 'num_movie': 2 }
          {'_id': 'Robert Zemeckis', 'num_movie': 1 }
** example 1:
$ db.movie.aggregate([{$group:{'_id': '$directed_by', 'num_movie':{$avg:$likes}}}])
** example 2:
$ db.tweets.aggregate([
     {'$group': {'_id':'$user.screen_name', 'count':{'$sum':1}}},
     {'$sort': {'count': -1}}])  # decendenting order
```
2. $match: Use the $match stage to filter documents.
```
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
3. $project: to do the math and project to be seen
```
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
4. $unwind -- Use to output a document for each element in the sizes array
```
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





