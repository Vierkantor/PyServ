#!/usr/bin/env python3

if False:
	import pytest
	import pymysql

	import dbclass

	class DBTestObject:
		"""A DB object that gets stored in a debug table."""
		@classmethod
		def _table_name(cls):
			return "test_{}".format(cls.__name__)

	@pytest.mark.incremental
	class TestDBClass:
		def test_make_dbclass(self):
			"""Makes a DBClass with two members and tests they can be read."""
			class Person(metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)
				full_name = dbclass.DBValue(str)

				def __init__(self, personal_name, full_name=None):
					self.personal_name = personal_name
					if full_name is None:
						full_name = personal_name
					self.full_name = full_name

			assert "personal_name" in Person._fields
			assert "full_name" in Person._fields

			johann = Person("Johann", "Johann Gambolputty")

			assert johann.personal_name == "Johann"
			assert johann.full_name == "Johann Gambolputty"

		def test_store_query_dbclass(self):
			"""Creates a query to store a DBClass with a single entry."""
			class Person(metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)
				def __init__(self, personal_name, full_name=None):
					self.personal_name = personal_name

			johann = Person("Johann")
			assert johann._store_query() == ("INSERT INTO `Person` SET `personal_name`=%s", ["Johann"])

			# now we'll act as if it was stored
			johann._inDB = True
			johann._id = 1
			assert johann._store_query() == ("UPDATE `Person` SET `personal_name`=%s WHERE `Person_id`=%s", ["Johann", 1])
			# we don't want to save it so mark it clean
			johann._dirty = False

		def test_prepare_table(self):
			"""Create a table to store an object."""
			class Person(metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)
			assert Person._prepare_table_query() == "CREATE TABLE IF NOT EXISTS `Person` (`Person_id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, `personal_name` text NOT NULL)"

		def test_store_dbclass(self):
			"""Actually store the value in a custom 'test' table."""
			class Person(DBTestObject, metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)
				full_name = dbclass.DBValue(str)

				def __init__(self, personal_name, full_name=None):
					self.personal_name = personal_name
					if full_name is None:
						full_name = personal_name
					self.full_name = full_name

			Person.prepare_table()
			karl = Person("Karl", "Karl Gambolputty")
			assert not karl._inDB
			assert karl._dirty
			# let's not muck up the actual database
			assert karl._table_name() == "test_Person"
			karl.store()
			assert karl._inDB
			assert not karl._dirty
			assert karl._id is not None

			# and get rid of the table
			with dbclass.connection as cursor:
				cursor.execute("DROP TABLE `{}`".format(karl._table_name()))

		def test_load_query(self):
			class Person(metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)

			assert Person._load_query(1) == ("SELECT `personal_name` FROM `Person` WHERE `Person_id`=%s", 1)

		def test_load(self):
			"""Get a value from the database."""
			class Person(metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)
				full_name = dbclass.DBValue(str)

				def __init__(self, personal_name, full_name=None):
					# __init__ should not be called when loading
					assert False

			johann = Person.load(2)
			assert johann._inDB
			assert not johann._dirty
			assert johann._id == 2
			assert johann.personal_name == "Johann"

		def test_store_and_load(self):
			"""Make an object, store it, and compare it with the loaded object."""
			class Person(DBTestObject, metaclass=dbclass.DBClass):
				personal_name = dbclass.DBValue(str)
				full_name = dbclass.DBValue(str)

				def __init__(self, personal_name, full_name=None):
					self.personal_name = personal_name
					if full_name is None:
						full_name = personal_name
					self.full_name = full_name

			Person.prepare_table()
			karl = Person("Karl", "Karl Gambolputty")
			karl.store()
			
			karl2 = Person.load(karl._id)
			assert karl.personal_name == karl2.personal_name
			assert karl.full_name == karl2.full_name

			# and get rid of the table
			with dbclass.connection as cursor:
				cursor.execute("DROP TABLE `{}`".format(karl._table_name()))

		def test_load_nonexistant_table(self):
			"""Make sure we can't load values from tables that don't exist."""
			class DoesNotExist(DBTestObject, metaclass=dbclass.DBClass):
				improbability = dbclass.DBValue(int)

			with pytest.raises(pymysql.ProgrammingError) as error:
				DoesNotExist.load(1)
			error.match("Table .* doesn't exist")

		def test_store_and_load_unicode(self):
			"""Check that MySQL doesn't mangle unicode characters.
			
			Strings with all kinds of characters in them should be identical after a round-trip.
			"""
			class UnicodeData(DBTestObject, metaclass=dbclass.DBClass):
				data = dbclass.DBValue(str)
				def __init__(self, data):
					self.data = data
			UnicodeData.prepare_table()
			test_strings = [
					"Hello, World!", # a very boring string
					"'\"`;\n\r\t \0 OR 'a'=='a';--", # mysql control characters
					"", # empty string
					"Algoriþmus Dĳkstræ", # ligatures
					"¡Hölå, sèñór!", # diacritics
					"e\u0301 != é", # combining character vs precomposed
					"→at← the 💻Web📱Cie it's 🕐always🕗 a 🎉", # emoji (multilingual plane ones)
			]

			for string in test_strings:
				original = UnicodeData(string)
				original.store()
				roundtrip = UnicodeData.load(original._id)
				assert original.data == roundtrip.data

			# and get rid of the table
			with dbclass.connection as cursor:
				cursor.execute("DROP TABLE `{}`".format(UnicodeData._table_name()))

		def test_store_and_load_int(self):
			"""Check that MySQL doesn't destroy int values."""
			class IntWrapper(DBTestObject, metaclass=dbclass.DBClass):
				data = dbclass.DBValue(int)
				def __init__(self, data):
					self.data = data
			IntWrapper.prepare_table()

			for exponent in range(0, 10):
				original = IntWrapper(10**exponent)
				original.store()
				roundtrip = IntWrapper.load(original._id)
				assert original.data == roundtrip.data

			# and get rid of the table
			with dbclass.connection as cursor:
				cursor.execute("DROP TABLE `{}`".format(IntWrapper._table_name()))

		def test_subclasses(self):
			"""What happens when making subclasses?"""
			class ParentClass(DBTestObject, metaclass=dbclass.DBClass):
				data1 = dbclass.DBValue(str)
				def __init__(self, data1):
					self.data1 = data1
			ParentClass.prepare_table()
			class ChildClass(ParentClass):
				data2 = dbclass.DBValue(int)
				def __init__(self, data1, data2):
					self.data2 = data2
					ParentClass.__init__(self, data1)
			ChildClass.prepare_table()
			parent = ParentClass("parent")
			child = ChildClass("child", 1)
			parent.store()
			child.store()
			parent_roundtrip = ParentClass.load(parent._id)
			child_roundtrip = ChildClass.load(child._id)
			assert parent.data1 == parent_roundtrip.data1
			assert child.data1 == child_roundtrip.data1
			assert child.data2 == child_roundtrip.data2

			# and get rid of the table
			with dbclass.connection as cursor:
				cursor.execute("DROP TABLE `{}`".format(ParentClass._table_name()))
				cursor.execute("DROP TABLE `{}`".format(ChildClass._table_name()))
