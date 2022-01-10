from .mysqlAttributesTranslator import MysqlAttributesTranslator
from .mysqlConditionsTranslator import MysqlConditionsTranslator
from .mysqlEntityStorage import EntityQueringException
from .mysqlStorage import MysqlStorage

from temod.core.base.attribute import Attribute
from temod.core.base.condition import Condition
from temod.core.base.entity import Entity
from temod.core.base.join import Join

#############################################

# EXCEPTIONS

class JoinedStorageException(Exception):
	"""docstring for GroupStorageException"""
	def __init__(self, *args, **kwargs):
		super(JoinedStorageException, self).__init__(*args, **kwargs)


#############################################

# MAIN CLASS

class MysqlJoinedStorage(MysqlStorage):
	"""docstring for MysqlJoinedStorage"""
	def __init__(self, joined_entity, base_entity, *relations,**kwargs):
		super(MysqlJoinedStorage, self).__init__(**kwargs)
		try:
			assert(issubclass(joined_entity,Join))
			self.joined_entity = joined_entity
		except AssertionError:
			raise JoinedStorageException("joined_entity must be a subclass of Join")
		try:
			assert(issubclass(base_entity,Entity))
			self.base_entity = base_entity
		except AssertionError:
			raise JoinedStorageException("base_entity must be a subclass of Entity")
		self.entities_list = [self.base_entity]
		try:
			assert(all([issubclass(relation[0],Entity) for relation in relations]))
			assert(all([issubclass(type(relation[1]),Condition) for relation in relations]))
			self.relations = relations
			[self.entities_list.append(relation[0]) for relation in relations]
		except AssertionError:
			raise JoinedStorageException("relations must be a tuple (EntityType,Condition)")
		self.attr_translator = MysqlAttributesTranslator()
		self.cond_translator = MysqlConditionsTranslator()

	#############################################

	# VERIFICATIONS

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

	#############################################

	# SQL BUILDERS

	def _build_join(self):
		join_query = ""
		for join in self.relations:
			join_query += f" JOIN {join[0].ENTITY_NAME} ON {self.cond_translator.translate(join[1])}"
		return join_query

	def _build_selection(self):
		return ", ".join([
			",".join([f"{entity.ENTITY_NAME}.{id_} as {entity.ENTITY_NAME}__{id_}" for id_ in entity.ATTRIBUTES])
			for entity in self.entities_list
		])

	#############################################

	# BASIC OPERATIONS

	def get(self,*ids,orderby=None,skip=None):
		self.verify_attributes(ids)

		ids = [(attr.name,self.attr_translator.translate(attr),attr.owner_name) for attr in ids]
		condition = " and ".join([
			(f'{self.base_entity.ENTITY_NAME if id_[2] is None else id_[2]}.{id_[0]}'+
			(" is " if id_[1] == "null" else "=")+id_[1])
			for id_ in ids
		])
		query = f"SELECT {self._build_selection()} FROM {self.base_entity.ENTITY_NAME} {self._build_join()} WHERE {condition}"

		result = self.getOne(query)
		if result is not None:
			return self.joined_entity.from_dict({
				entity.ENTITY_NAME:entity.from_dict({
					col.replace(f'{entity.ENTITY_NAME}__',''):value for col,value in result.items() if col.startswith(f'{entity.ENTITY_NAME}__')
				}) for entity in self.entities_list
			})


	def list(self,*ids,orderby=None,skip=None,limit=None):
		self.verify_attributes(ids)

		ids = [(attr.name,self.attr_translator.translate(attr),attr.owner_name) for attr in ids]
		condition = None
		if len(ids) > 0:
			condition = " and ".join([
				(f'{self.base_entity.ENTITY_NAME if id_[2] is None else id_[2]}.{id_[0]}'+
				(" is " if id_[1] == "null" else "=")+id_[1])
				for id_ in ids
			])
		query = f"SELECT {self._build_selection()} FROM {self.base_entity.ENTITY_NAME} {self._build_join()}"

		for row in self.searchMany(query,condition=condition,orderby=orderby,skip=skip,limit=limit):
			yield self.joined_entity.from_dict({
				entity.ENTITY_NAME:entity.from_dict({
					col.replace(f'{entity.ENTITY_NAME}__',''):row[col] for col in row if col.startswith(f'{entity.ENTITY_NAME}__')
				}) for entity in self.entities_list
			})

	#############################################


	def conditionnedList(self,condition,orderby=None,skip=None,limit=None):
		self.verify_condition(condition)
		query = f"SELECT {self._build_selection()} FROM {self.base_entity.ENTITY_NAME} {self._build_join()}"
		for row in self.searchMany(query,condition=f"{self.cond_translator.translate(condition)}",orderby=orderby,skip=skip,limit=limit):
			yield self.joined_entity.from_dict({
				entity.ENTITY_NAME:entity.from_dict({
					col.replace(f'{entity.ENTITY_NAME}__',''):row[col] for col in row if col.startswith(f'{entity.ENTITY_NAME}__')
				}) for entity in self.entities_list
			})


#############################################



		