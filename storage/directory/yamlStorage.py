from .directoryStorage import DirectoryStorage
from Temod.core.base.entity import Entity

import yaml


class YamlStorage(DirectoryStorage):
	"""docstring for YamlStorage"""
	def __init__(self, directory, mode="", encoding="utf-8",createDir=False):
		super(YamlStorage, self).__init__(directory,mode="",encoding=encoding,createDir=createDir)

	def save(self, id_, dict_, encoding=None):
		self.write(id_, yaml.dump(dict_), encoding=encoding if not encoding is None else self.encoding)

	def load(self, id_, encoding=None):
		return yaml.safe_load(self.read(id_,encoding=encoding if not encoding is None else self.encoding))

	def list(self, skip=None, limit=None):
		nb = -1; sent = 0;
		for file in self.content(only_files=True):
			nb += 1
			if skip is not None and nb <= skip:
				continue
			if limit is not None and sent == limit:
				break
			sent += 1
			yield self.load(file)


class YamlEntityStorage(YamlStorage):
	"""docstring for YamlEntityStorage"""
	def __init__(self, directory, entity_type, **kwargs):
		super(YamlEntityStorage, self).__init__(directory,**kwargs)
		try:
			assert(issubclass(entity_type,Entity))
			self.entity_type = entity_type
		except AssertionError:
			raise EntityStorageException(f"Entity type {entity_type.__name__} is not a subclass of Entity")

	#############################################

	# VERIFICATIONS

	def verify_entity(self,entity):
		try:
			assert(issubclass(type(entity),self.entity_type))
		except AssertionError:
			raise EntityStorageException(f"Entity type {type(entity).__name__} cannot be stored in Entity {self.entity_type.__name__} storage")
		
	#############################################

	def create(self, entity):
		self.verify_entity(entity)
		ids = [value for attr,value in entity.attributes.items() if value.id_id]
		if len(ids) > 1 or len(ids) == 0:
			raise YamlEntityStorageException("Only entites with one identifier can be stored")
		id_ = ids[0]
		if not issubclass(type(id_),StringAttribute) and not issubclass(type(id_),IntegerAttribute):
			raise YamlEntityStorageException("Only entites with string or integer identifier can be stored")
		self.save(str(id_.value),entity.to_dict())
		return id_

	def get(self, *ids):
		if len(ids) == 0 or len(ids) > 0:
			raise YamlEntityStorageException("Exactely one identifier is required to fetch entity.")
		return self.entity_type.from_dict(self.load(str(ids[0].value)))

	def list(self, skip=None, limit=None):
		nb = -1; sent = 0;
		for file in self.content(only_files=True):
			nb += 1
			if skip is not None and nb <= skip:
				continue
			if limit is not None and sent == limit:
				break
			sent += 1
			yield self.entity_type.from_dict(self.load(file))