import sqlite3

class myDatabase:
	def open(self, filepath):
		self.conn = None
		self.conn = sqlite3.connect(filepath)
		self.cur = self.conn.cursor()
		
	def close(self):
		self.cur.close()
		self.conn.close()
	
	def addTable(self, tableName, fields):
		strSql = 'DROP TABLE IF EXISTS ' + tableName + ' '
		self.cur.execute(strSql)
		self.conn.commit()
		
		myFieldString = ''
		for row in fields:
			myFieldString = myFieldString + row[0] + ' ' + row[1] + ', '

		myFieldString = myFieldString[:-2]
		strSql = 'CREATE TABLE ' + tableName + ' (' + myFieldString + ')'
		self.cur.execute(strSql)
		self.conn.commit()
		
	def deleteTable(self, tableName):
		strSql = 'DROP TABLE IF EXISTS ' + tableName + ' '
		self.cur.execute(strSql)
		self.conn.commit()
	
	def addColumns(self, tableName, fields):
		for row in fields:
			strSql = 'ALTER TABLE ' + tableName + ' ADD COLUMN ' + row[0] + ' ' + row[1]
			self.cur.execute(strSql)
		self.conn.commit()

	def addRecord(self, tableName, fields, data):
		dataLength = len(fields)
		strFields = ''
		strValues = ''
		for i in range(dataLength):
			strFields = strFields + fields[i] + ','
			strValues = strValues + '?,'
		strFields = strFields[:-1]
		strValues = strValues[:-1]
		strSql = 'INSERT INTO '+ tableName + '(' + strFields + ')\r\nVALUES (' + strValues + ');'
		self.cur.execute(strSql, data)
		self.conn.commit()

		return self.cur.lastrowid

	def updateRecord(self, record, tableName, columns, data):
		strSql = 'UPDATE ' + tableName + '\r\nSET '
		for colName in columns:
			strSql = strSql + colName + ' = ?,\r\n'
		strSql = strSql[:-3]
		if isinstance(record['idx'],str):
			strSql = strSql + '\r\nWHERE ' + record['key'] + ' = "' + str(record['idx']) + '"'
		else:
			strSql = strSql + '\r\nWHERE ' + record['key'] + ' = ' + str(record['idx'])
		self.cur.execute(strSql, data)
		self.conn.commit()
	
	def deleteRecord(self, record, tableName):
		strSql = 'DELETE FROM ' + tableName + ' WHERE ' + record['key'] + '=' + str(record['idx'])
		self.cur.execute(strSql)
		self.conn.commit()

	def getTableData(self, tableName):
		strSql = 'SELECT * FROM ' + tableName
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def getTableDataSorted(self, tableName, sortCol, sortOrder):
		# Parameter Name	Data Type			Description
		# tableName			string				Table containing the data being queried
		# sortCol			string				Column Name used to sort the data
		# sortOrder			string				'ASC' for Ascending, 'DESC' for descending
		strSql = 'SELECT * FROM ' + tableName + '\r\nORDER BY ' + sortCol + ' ' + sortOrder
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def queryTableData(self, tableName, conditions):
		# Parameter Name	Data Type			Description
		# tableName			string				Table containing the data being queried
		# columns			list[string]		Columns to return in the query
		# conditions		array[dict]			Conditions to apply to the query
		#						'condition'		Boolean expression in SQLite
		#						'operator'		AND / OR, leave blank for first condition
		strSql = 'SELECT *\r\nFROM ' + tableName + '\r\n' + 'WHERE '
		strFirstCond = conditions.pop(0)
		strSql = strSql + strFirstCond['condition'] + '\r\n'
		for row in conditions:
			strSql = strSql + row['operator'] + ' ' + row['condition'] + '\r\n'
		strSql = strSql + ';'
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def queryTableDataSorted(self, tableName, conditions, sortCol, sortOrder):
		# Parameter Name	Data Type			Description
		# tableName			string				Table containing the data being queried
		# columns			list[string]		Columns to return in the query
		# conditions		array[dict]			Conditions to apply to the query
		#						'condition'		Boolean expression in SQLite
		#						'operator'		AND / OR, leave blank for first condition
		# sortCol			string				Column Name used to sort the data
		# sortOrder			string				'ASC' for Ascending, 'DESC' for descending
		strSql = 'SELECT *\r\nFROM ' + tableName + '\r\n' + 'WHERE '
		strFirstCond = conditions.pop(0)
		strSql = strSql + strFirstCond['condition'] + '\r\n'
		for row in conditions:
			strSql = strSql + row['operator'] + ' ' + row['condition'] + '\r\n'
		strSql = strSql + ';'
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def getColumnData(self, tableName, columns):
		strSql = 'SELECT '
		for column in columns:
			strSql = strSql + column + ', '
		strSql = strSql[:-2] + '\r\nFROM ' + tableName
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def queryColumnData(self, tableName, columns, conditions):
		# Parameter Name	Data Type			Description
		# tableName			string				Table containing the data being queried
		# columns			list[string]		Columns to return in the query
		# conditions		array[dict]			Conditions to apply to the query
		#						'condition'		Boolean expression in SQLite
		#						'operator'		AND / OR, leave blank for first condition
		strSql = 'SELECT '
		for i in range(len(columns)):
			strSql = strSql + columns[i] + ', '
		strSql = strSql[:-2] + '\r\nFROM ' + tableName + '\r\n' + 'WHERE '
		strFirstCond = conditions.pop(0)
		strSql = strSql + strFirstCond['condition'] + '\r\n'
		for row in conditions:
			strSql = strSql + row['operator'] + ' ' + row['condition'] + '\r\n'
		strSql = strSql + ';'
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def getRecord(self, tableName, record):
		strSql = 'PRAGMA table_info("{}")'.format(tableName)
		tableColumns = self.mySqlQuery(strSql)
		strSql = 'SELECT * FROM {}\r\nWHERE {} = "{}"'.format(tableName,record['key'],record['idx'])
		rows = self.mySqlQuery(strSql)
		if len(rows) == 0:
			return None
		else:
			i=0
			response = {}
			for item in tableColumns:
				response[item[1]] = rows[0][i]
				i+=1
			return response

	def mySqlQuery(self, strSql):
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return rows

	def RecordExists(self,table,record):
		strSql = 'SELECT * FROM {}\r\nWHERE {} = "{}"'.format(table,record['key'],record['idx'])
		self.cur.execute(strSql)
		rows = self.cur.fetchall()
		return True if len(rows) == 1 else False
		pass

class queryBuilder():
	def __init__(self):
		self.strSql = ''
	
	def add_selection(self, tableName, columns=[]):
		self.strSql = self.strSql + 'SELECT '
		self.strSql = self.strSql + ', '.join(columns) if len(columns) > 0 else self.strSql + '*'
		self.strSql = self.strSql + ' FROM {}'.format(tableName)
	
	def add_statement(self, statement):
		self.strSql = self.strSql + '\r\n' + statement

	def add_sorting(self, sortCol, ascending=True):
		strAsc = 'ASC' if ascending else 'DESC'
		self.strSql = self.strSql + '\r\n' + 'ORDER BY {} {}'.format(sortCol,strAsc)

	def get_string(self):
		return self.strSql

if __name__ == "__main__":
	#myString = queryBuilder()
	#myString.add_selection('InvAccounts', ['Josh','Staci','Meredith','Elaina'])
	#myString.add_statement('WHERE ACTIVE = 1')
	#myString.add_sorting('Position')
	#print(myString.get_string())
	qFilenameDb = r'C:\Users\joshm\OneDrive\Documents\Josh\03_Financial\Database\ExpenseTracking_20231215.db'
	db = myDatabase()
	db.open(qFilenameDb)
	#result = db.RecordExists('Assets',{'key': 'symbol', 'idx': 'QQQ'})
	result = db.getRecord('Assets',{'key': 'symbol', 'idx': 'VOO'})
	db.close()
	pass