import pymysql

import config

"""Maps py-type -> sql-type."""
database_types = {
		int: "int(11)",
		float: "float",
		str: "text",
}

class DBValue:
	"""A value that can be stored directly in the database.

	Takes a python type as argument, but if it isn't supported throws TypeError.
	Used in combination with DBClass.
	"""
	def __init__(self, type):
		self.name = None
		self.attr = None
		self.check_type(type)
		self.type = type

	def check_type(self, type):
		"""Verify that this type can be stored in the database.
		
		If it isn't supported as a field in the dabase,
		we throw a TypeError
		"""
		if type not in database_types:
			raise TypeError("can't store {} as database field".format(type))

	def sql_type(self):
		return database_types[self.type]

	def __get__(self, inst, cls):
		if inst is None:
				return self
		else:
			return inst.__dict__[self.attr]

	def __set__(self, inst, value):
		if not isinstance(value, self.type):
			raise TypeError("wrong type {} for {}".format(type(value), self.name))
		else:
			inst.__dict__[self.attr] = value

	def __repr__(self):
		return "DBValue {} : {} <{}>".format(self.name, self.type, self.attr)

def backticks(string):
	"""Write backticks around a string."""
	return "`{}`".format(string)

class DBConnected:
	"""A mixin that DBClass uses to serialize/deserialize database values.
	"""

	"""Has this object already been stored in the database?"""
	_inDB = False
	"""The unique identifier for the object within its class."""
	_id = None
	"""Has this object been modified before it was stored in the database?"""
	_dirty = True

	def __del__(self):
		if self._dirty and self._inDB:
			raise ValueError("DBObject destructed before updates being stored!")

	@classmethod
	def _table_name(cls):
		"""Return the name of the table that this object is stored in."""
		return cls.__name__

	@classmethod
	def _id_field(cls):
		"""Return the field that this object's id is stored in."""
		return "{}_id".format(cls._table_name())

	@classmethod
	def _load_row(cls, id, row):
		"""After a query has returned a row, load it into an instance of this class.
		
		This does not call __init__ so you can keep using it for constructing a new instance.
		"""
		# bypass __init__
		obj = cls.__new__(cls)
		for (name, attr), value in zip(cls._fields.items(), row):
			attr.__set__(obj, value)
		obj._id = id
		obj._inDB = True
		obj._dirty = False
		return obj

	@classmethod
	def _load_query_components(cls):
		"""Get the basic components of a load query.
		
		Returns a tuple (table : str, fields : list, id_field : str)
		"""
		table = backticks(cls._table_name())
		fields = []
		for name, attr in cls._fields.items():
			field = backticks(name)
			fields.append(field)
		return table, fields, backticks(cls._id_field())

	@classmethod
	def _load_query(cls, id):
		"""Give a query for loading the object with the given id."""
		table, fields, id_field = cls._load_query_components()
		return "SELECT {} FROM {} WHERE {}=%s".format(", ".join(fields), table, id_field), id

	@classmethod
	def load(cls, id):
		"""Load an instance of this class from the database."""
		query, args = cls._load_query(id)
		with connection as cursor:
			cursor.execute(query, args)
			row = cursor.fetchone()
		return cls._load_row(id, row)

	@classmethod
	def prepare_table(cls):
		"""Ensure a table exists to store the objects in."""
		query = cls._prepare_table_query()
		with connection as cursor:
			cursor.execute(query)

	@classmethod
	def _prepare_table_query(cls):
		"""Make a query to ensure the table exists."""
		table_name = backticks(cls._table_name())
		columns = [
			"{} int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY".format(backticks(cls._id_field()))
		]
		for name, attr in cls._fields.items():
			field = backticks(name)
			type = attr.sql_type()
			columns.append("{} {} NOT NULL".format(field, type))
		return "CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, ", ".join(columns))

	def store(self):
		"""Store this object in the database."""
		# only store dirty values
		if self._inDB and not self._dirty:
			return

		query, args = self._store_query()
		# TODO: recursion
		with connection as cursor:
			cursor.execute(query, args)
		if not self._inDB:
			cursor.execute("SELECT LAST_INSERT_ID()");
			self._inDB = True
			self._id = cursor.fetchall()[0][0];
		self._dirty = False

	def _store_query(self):
		"""Make a query that stores this object in the database."""
		if self._inDB:
			return self._update_query()
		else:
			return self._insert_query()

	def _store_query_components(self):
		"""Get the basic components of a store query.
		
		Returns a tuple (table : str, assignments : list, values : list)
		"""
		table = backticks(self._table_name())
		values = []
		assignments = []
		for name, attr in type(self)._fields.items():
			field = backticks(name)
			value_format = "%s"
			assignments.append("{}={}".format(field, value_format))
			values.append(attr.__get__(self, type(self)))
		return table, assignments, values

	def _insert_query(self):
		"""Make a query that inserts a new row with this value."""
		table, assignments, values = self._store_query_components()
		return "INSERT INTO {} SET {}".format(table, ", ".join(assignments)), values

	def _update_query(self):
		"""Make a query that replaces the values of the DBObject with the current ones."""
		table, assignments, values = self._store_query_components()
		values.append(self._id)
		id_field = self._id_field()
		return "UPDATE {} SET {} WHERE {}=%s".format(table, ", ".join(assignments), backticks(id_field)), values

"""Map name -> class for DBClasses, so their tables can automatically be generated."""
stored_classes = {}

def prepare_tables():
	"""Create all the tables for the stored DBClasses.
	
	When starting up an app, you can call prepare_tables()
	to make sure all tables this app requires, are available.
	This requires that you don't programmatically create new DBClasses.
	"""
	for cls in stored_classes.values():
		cls.prepare_table()

class DBClass(type):
	"""Metaclass for a Python object that can be stored in the database.
	
	When starting up an app, you can call prepare_tables()
	to make sure all tables this app requires, are available.
	This requires that you don't programmatically create new DBClasses.
	
	Examples:
		class Person(metaclass=DBClass):
			personal_name = DBValue(str)
			full_name = DBValue(str)
	"""
	def __init__(self, name, bases, attrs):
		super(DBClass, self).__init__(name, bases, attrs)
		stored_classes[name] = self

	def __new__(metacls, cls, bases, clsdict):
		"""Construct a new class stored in the database."""
		fields = {}
		for name, attr in clsdict.items():
			if isinstance(attr, DBValue):
				attr.name = name
				attr.attr = '_{}'.format(name)
				fields[name] = attr
		# copy over the base class's fields
		# TODO: throw exception in the case of duplicate fields
		for base in bases:
			try:
				base_fields = base._fields
			except AttributeError:
				continue
			fields.update(base_fields)
		clsdict["_fields"] = fields
		return super().__new__(metacls, cls, bases + (DBConnected,), clsdict)

# connect using utf8mb4 because we want to store emoji
connection = pymysql.connect(charset='utf8mb4', **config.database_settings)
