class MalformedConditionException(Exception):
	"""docstring for MalformedConditionException"""
	def __init__(self, *args, **kwargs):
		super(MalformedConditionException, self).__init__(*args, **kwargs)
		
#################################################

class Condition(object):
	"""docstring for Condition"""
	def __init__(self):
		super(Condition, self).__init__()

class And(Condition):
	"""docstring for And"""
	def __init__(self,*conditions,**kwargs):
		super(And, self).__init__(**kwargs)
		try:
			assert(all([issubclass(type(condition),Condition) for condition in conditions]))
		except AssertionError:
			raise MalformedConditionException("condition must be a subclass of Condition")
		self.conditions = conditions

class Or(Condition):
	"""docstring for Or"""
	def __init__(self,*conditions,**kwargs):
		super(Or, self).__init__(**kwargs)
		try:
			assert(all([issubclass(type(condition),Condition) for condition in conditions]))
		except AssertionError:
			raise MalformedConditionException("condition must be a subclass of Condition")
		self.conditions = conditions

#################################################

class Equals(Condition):
	"""docstring for Equals"""
	def __init__(self,field1,field2,**kwargs):
		super(Equals, self).__init__(**kwargs)
		self.field1 = field1
		self.field2 = field2

#################################################

class StartsWith(Condition):
	"""docstring for StartsWith"""
	def __init__(self,field,case_sensitive=True,**kwargs):
		super(StartsWith, self).__init__(**kwargs)
		self.field = field
		self.case_sensitive = case_sensitive

#################################################

class In(Condition):
	"""docstring for In"""
	def __init__(self,field,*values,**kwargs):
		super(In, self).__init__(**kwargs)
		self.field = field
		self.values = values
		