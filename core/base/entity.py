from .attribute import Attribute

class MalformedEntityException(object):
	"""docstring for MalformedEntityException"""
	def __init__(self, *args, **kwargs):
		super(MalformedEntityException, self).__init__(*args, **kwargs)


class Entity(object):
	"""docstring for Entity"""
	def __init__(self, *attributes):
		super(Entity, self).__init__()
		self.attributes = {attribute.name:attribute for attribute in attributes}
		self.snapshot = None
		try:
			assert(all([issubclass(type(attribute),Attribute) for attribute in attributes]))
		except AssertionError:
			raise MalformedEntityException("Some attributes are not subclasses of Attribute")

	#####################################################

	def setAttribute(self,attribute,value):
		self.attributes[attribute].set_value(value)

	def setAttributes(self,**kwargs):
		for k,v in kwargs.items():
			self.attributes[k].set_value(v)

	def __getattribute__(self,name): 
		try:
			if name != "attributes":
				return self.attributes[name].value
		except:
			pass
		return super(Entity,self).__getattribute__(name)

	#####################################################

	def takeSnapshot(self):
		self.snapshot = {
			name:type(attribute)(attribute.name,value=attribute.value)
			for name,attribute in self.attributes.items()
		}
		return self

	#####################################################

	def to_dict(self):
		return {
			name:attr.to_scalar()
			for name,attr in self.attributes.items()
		}

	def __repr__(self):
		attributes = [f"{attr.name} ({type(attr).__name__}): {attr.value} ({type(attr.value).__name__})" for attr in self.attributes.values()]
		return f"""Entity {self.ENTITY_NAME}"""+((":\n\t"+"\n\t".join(attributes)) if len(self.attributes) > 0 else "")

	#####################################################