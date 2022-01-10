from temod.core.base.attribute import Attribute
from temod.core.base.condition import Condition
from temod.core.base.relation import Relation
from temod.core.base.entity import Entity

from .mysqlAttributesTranslator import MysqlAttributesTranslator
from .mysqlConditionsTranslator import MysqlConditionsTranslator
from .mysqlStorage import MysqlStorage

class EntityStorageException(Exception):
	"""docstring for EntityStorageException"""
	def __init__(self, *args, **kwargs):
		super(EntityStorageException, self).__init__(*args, **kwargs)

class EntitySnapshotException(Exception):
	"""docstring for EntitySnapshotException"""
	def __init__(self, *args, **kwargs):
		super(EntitySnapshotException, self).__init__(*args, **kwargs)

class EntityQueringException(Exception):
	"""docstring for EntityQueringException"""
	def __init__(self, *args, **kwargs):
		super(EntityQueringException, self).__init__(*args, **kwargs)

class EntityRelationException(Exception):
	"""docstring for EntityRelationException"""
	def __init__(self, *args, **kwargs):
		super(EntityRelationException, self).__init__(*args, **kwargs)

class MysqlEntityStorage(MysqlStorage):
	"""docstring for MysqlEntityStorage"""
	def __init__(self, entity_type,external_relations=None,**kwargs):
		super(MysqlEntityStorage, self).__init__(**kwargs)
		if external_relations is None:
			external_relations = {}
		try:
			assert(issubclass(entity_type,Entity))
			self.entity_type = entity_type
		except AssertionError:
			raise EntityStorageException(f"Entity type {entity_type.__name__} is not a subclass of Entity")
		try:
			assert(all([issubclass(type(relation),Relation) for relation in external_relations.values()]))
			self.relations = external_relations
		except AssertionError:
			raise EntityRelationException("Relations must be subclass of Relation")
		self.attr_translator = MysqlAttributesTranslator()
		self.cond_translator = MysqlConditionsTranslator()

	#############################################

	# VERIFICATIONS

	def verify_entity(self,entity):
		try:
			assert(issubclass(type(entity),self.entity_type))
		except AssertionError:
			raise EntityStorageException(f"Entity type {type(entity).__name__} cannot be stored in Entity {self.entity_type.__name__} storage")
		
	def verify_attributes(self,attributes):
		try:
			assert(all([issubclass(type(attribute),Attribute) for attribute in attributes]))
		except AssertionError:
			raise EntityQueringException(f"Conditions must all be subtype of Attribute")

	def verify_condition(self,condition):
		try:
			assert(issubclass(type(condition),Condition))
		except AssertionError:
			raise EntityQueringException(f"Conditions must all be subtype of Attribute")

	##############################################

	##############################################

	# SINGLE TABLE & ROWS OPERATIONS

	def get(self,*ids):
		self.verify_attributes(ids)
		ids = [(attr.name,self.attr_translator.translate(attr)) for attr in ids]
		condition = " and ".join([id_[0]+(" is " if id_[1] == "null" else "=")+id_[1] for id_ in ids])
		query = f"SELECT * FROM {self.entity_type.ENTITY_NAME} WHERE {condition}"
		result = self.getOne(query)
		if result is not None:
			return self.entity_type.from_dict(result)

	def delete(self,*ids,many=False):
		self.verify_attributes(ids)
		ids = [(attr.name,self.attr_translator.translate(attr)) for attr in ids]
		condition = " and ".join([id_[0]+(" is " if id_[1] == "null" else "=")+id_[1] for id_ in ids])
		query = f"DELETE FROM {self.entity_type.ENTITY_NAME} WHERE {condition}"
		if not many:
			query += " LIMIT 1"
		return self.executeAndCommit(query).lastrowid

	def create(self,entity):
		self.verify_entity(entity)
		values = [
			(attr,self.attr_translator.translate(value)) 
			for attr,value in entity.attributes.items() if not value.is_auto
		]
		query = f"INSERT INTO {entity.ENTITY_NAME} ({','.join([v[0] for v in values])}) VALUES ({','.join([v[1] for v in values])})"
		return self.executeAndCommit(query).lastrowid

	def update(self,entity,attributes=None,updateID=False):
		self.verify_entity(entity)
		toUpdate = [] if attributes is None else attributes
		values = [
			(attr,self.attr_translator.translate(value)) 
			for attr,value in entity.attributes.items() 
			if not value.is_auto and attr in toUpdate and (updateID or not value.is_id)
		]
		ids = [
			(attr,self.attr_translator.translate(value))
			for attr,value in entity.attributes.items()
			if value.is_id
		]
		condition = " and ".join([i[0]+"="+i[1] for i in ids])
		query = f"UPDATE {entity.ENTITY_NAME} SET {','.join([v[0]+(' is ' if v[1] == 'null' else '=')+v[1] for v in values])} WHERE {condition}"
		return self.executeAndCommit(query).lastrowid

	def list(self,*ids,orderby=None,skip=None,limit=None):
		self.verify_attributes(ids)
		base = f'SELECT * FROM {self.entity_type.ENTITY_NAME}'
		if len(ids) > 0:
			values = [(v.name,self.attr_translator.translate(v)) for v in ids]
			condition = " and ".join([v[0]+(" is " if v[1] == "null" else "=")+v[1] for v in values])
		else:
			condition = None
		for row in self.searchMany(base,condition=condition,orderby=orderby,skip=skip,limit=limit):
			yield self.entity_type.from_dict(row) 

	##############################################

	##############################################

	# SINGLE TABLE CONDITIONNED OPERATIONS

	def conditionnedCount(self,condition):
		self.verify_condition(condition)
		query = f'SELECT count(*) FROM {self.entity_type.ENTITY_NAME} WHERE {self.cond_translator.translate(condition)}'
		result = self.getOne(query)
		if result is not None:
			return result.pop(list(result.keys())[0])

	def conditionnedList(self,condition,orderby=None,skip=None,limit=None):
		self.verify_condition(condition)
		base = f'SELECT * FROM {self.entity_type.ENTITY_NAME}'
		for row in self.searchMany(base,condition=f"{self.cond_translator.translate(condition)}",orderby=orderby,skip=skip,limit=limit):
			yield self.entity_type.from_dict(row)


	##############################################


	##############################################

	# SINGLE TABLE & MULTIPLE ROWS OPERATIONS

	def createMultiple(self,entities):
		[self.verify_entity(entity) for entity in entities]
		values = []
		columns = None
		for entity in entities:
			if columns is None:
				columns = [attr for attr,value in entity.attributes.items() if not value.is_auto]
			values.append('('+ ','.join([self.attr_translator.translate(entity.attributes[column]) for column in columns]) +')')
		query = f"INSERT INTO {entity.ENTITY_NAME} ({','.join([column for column in columns])}) VALUES {' ,'.join(values)}"
		return self.executeAndCommit(query).lastrowid
		
	##############################################
		
	##############################################

	# FURTHER FUNCTIONNALITIES

	def updateOnSnapshot(self,entity,updateID=False):
		self.verify_entity(entity)
		if entity.snapshot is None:
			raise EntitySnapshotException("No snapshot to recover data from")
		attributes = [
			attribute for attribute in entity.attributes
			if entity.snapshot[attribute].value != getattr(entity,attribute)
		]
		if len(attributes) > 0:
			self.update(entity,attributes=attributes,updateID=updateID)

		
	##############################################
		
	##############################################

	# MULTI TABLE OPERATIONS

	def mergeOn(self,*relations):
		try:
			assert(all([relation in self.relations for relation in relations]))
		except AssertionError:
			raise EntityRelationException("Can't merge on non existing relations")
		return MysqlMergedEntityStorage(
			self.entity_type,
			*[self.relations[relation] for relation in relations],
			connexion=self.connexion
		)
		
	##############################################