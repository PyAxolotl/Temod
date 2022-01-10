class RelationStructureException(Exception):
	"""docstring for RelationStructureException"""
	def __init__(self, *args,**kwargs):
		super(RelationStructureException, self).__init__(*args,**kwargs)

class Relation(object):
	"""docstring for Relation"""
	def __init__(self):
		super(Relation, self).__init__()		

class ForeignKeyRelation(Relation):
	"""docstring for BilateralRelation"""
	def __init__(self, start_node, end_node):
		super(BilateralRelation, self).__init__()
		self.entity1 = start_node[0]
		self.entity2 = end_node[0]
		self.attribute1 = start_node[1]
		self.attribute2 = end_node[1]
		try:
			assert(type(self.attribute1) is type(self.attribute2))
		except AssertionError:
			raise RelationStructureException("Entities must be linked on attributes of the same type")
		
	def has_entity(self,entity):
		return self.entity1 is entity or self.entity2 is entity