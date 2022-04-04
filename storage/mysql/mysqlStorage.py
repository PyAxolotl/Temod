import mysql.connector

class MysqlStorage():
	def __init__(self, user="",password="",host="",port=3306,database="",connexion=None):
		super(MysqlStorage, self).__init__()
		self.connexion = mysql.connector.connect(
			user=user, 
			password=password,
			host=host,
			port=port,
			database=database
		) if connexion is None else connexion
	
	def close(self):
		self.connexion.close()

	def executeAndCommit(self,query):
		cursor = self.connexion.cursor()
		try:
			cursor.execute(query)
			self.connexion.commit()
		finally:
			cursor.close()
		return cursor

	def getOne(self,query):
		cursor=self.connexion.cursor()
		try:
			query=(query)
			cursor.execute(query)
			result = cursor.fetchone()
			columns = cursor.column_names
		finally:
			cursor.close()
		if result is not None:
			return {col:result[i] for i,col in enumerate(columns)}

	def getMany(self,query):
		cursor=self.connexion.cursor()
		try:
			cursor.execute(query)
			columns = cursor.column_names
			for row in cursor.fetchall():
				yield {col:row[i] for i,col in enumerate(columns)}
		finally:
			cursor.close()

	def searchMany(self,select,condition=None,orderby=None,skip=None,limit=None):
		query = select
		if condition is not None:
			query += f' WHERE {condition}'
		if orderby is not None:
			query += f' ORDER BY {orderby}'
		if limit is not None:
			query += f' LIMIT {limit}'
			if skip is not None:
				query += f' OFFSET {skip}'
		for row in self.getMany(query):
			yield row
	