from pymongo import MongoClient


def getDb(dbName):
	client = MongoClient()
	return client[dbName]

	
def insert(db, tableName, insertJson):
	#db = getDb(dbName)
	result = db[tableName].insert(insertJson)
	return result
	

def delete(db, tableName, deleteJson):
	#db = getDb(dbName)
	result = db[tableName].remove(deleteJson)
	return result
	
	
def update_one(db, tableName, query, updateJson):
	#db = getDb(dbName)
	result = db[tableName].update(query, updateJson, upsert=True)
	return result
	
	
def search(db, tableName, query, snapshot=False):
	#db = getDb(dbName)
	table = db[tableName]
	cursor =  table.find(query, snapshot=snapshot)
	#ans = []
	#for doc in cursor:
	#	ans.append(doc)
	#return ans
	return cursor
	
	
def search_one(db, tableName, query):
	#db = getDb(dbName)
	table = db[tableName]
	cursor = table.find_one(query)
	return cursor

	
''' Counts the number of rows matching the query condition '''	
def count(db, tableName, query):
	#db = getDb(dbName)
	table = db[tableName]
	cursor = table.find(query).count()
	return cursor
	
	
''' Checks whether the search query given has atleast one row or not '''
def exists(db, tableName, query):
	cursor = count(db, tableName, query)
	if cursor == 0:
		return False
	return True
	
		   


	