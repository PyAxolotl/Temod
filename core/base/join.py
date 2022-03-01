from .entity import Entity


class MalformedJoinedEntity(Exception):
	"""docstring for MalformedJoinedEntity"""
	def __init__(self, *args, **kwargs):
		super(MalformedJoinedEntity, self).__init__(*args, **kwargs)


class Join(object):
	"""docstring for Join"""
	def __init__(self, *entities,**kwargs):
		super(Join, self).__init__()
		try:
			assert(all([issubclass(type(entity),Entity) for entity in entities]))
			self.entities = {entity.ENTITY_NAME:entity for entity in entities}
			assert(all([issubclass(type(entity),Entity) or entity is None for entity in kwargs.values()]))
			self.entities.update(kwargs)
		except AssertionError:
			raise MalformedJoinedEntity(
				f"entities must be a objects of type Entity not {','.join([type(entity).__name__ for entity in entities if not issubclass(type(entity),Entity)])}"
			)

	def __getattribute__(self,name): 
		try:
			if name != "entities":
				return self.entities[name]
		except:
			pass
		return super(Join,self).__getattribute__(name)

	def to_dict(self):
		return {
			name:entity.to_dict() for name,entity in self.entities.items()
		}



		