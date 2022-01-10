from datetime import datetime, date

import traceback
import base64
import uuid

BASE16_ALPHABET = "abcdef0123456789"
BASE64_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/="

class AttributeValueException(Exception):
	"""docstring for AttributeValueException"""
	def __init__(self, *args,**kwargs):
		super(AttributeValueException, self).__init__(*args,**kwargs)
		
class Attribute(object):
	"""docstring for Attribute"""
	def __init__(self, name, value_type, value=None, is_id=False,is_auto=False,is_nullable=True,default_value=None,force_cast=None,owner_name=None):
		super(Attribute, self).__init__()
		self.name = name
		self.is_id = is_id
		self.is_auto = is_auto
		self.value_type = value_type
		self.owner_name = owner_name
		self.is_nullable = is_nullable
		self.default_value = default_value		
		self.value = value if value is not None else default_value
		if force_cast is not None:
			try:
				self.value = force_cast(self.value)
			except:
				traceback.print_exc()
				raise AttributeValueException(f"Cannot force cast value {self.value}")

	def check_value(self):
		if not self.is_nullable and self.value is None:
			raise AttributeValueException("Non nullable attribute set to null.")
		if self.value is not None and not issubclass(type(self.value),self.value_type):
			raise AttributeValueException(f"Wrong value type {type(self.value).__name__} for {type(self).__name__} (attribute: {self.name})")

class StringAttribute(Attribute):
	"""docstring for StringAttribute"""
	def __init__(self, name, non_empty=False,force_lower_case=False,**kwargs):
		super(StringAttribute, self).__init__(name,str,**kwargs)
		self.non_empty = non_empty
		self.check_value()
		if force_lower_case:
			self.value = self.value.lower() if self.value is not None else self.value

	def check_value(self):
		super(StringAttribute,self).check_value()
		if self.non_empty and (self.value == "" or self.value == None):
			raise AttributeValueException("Value of non empty StringAttribute set to null or empty str")

class UUID4Attribute(StringAttribute):
	"""docstring for UUID4Attribute"""
	def __init__(self, *args, **kwargs):
		super(UUID4Attribute, self).__init__(*args, **kwargs)
		self.check_value()

	def check_value(self):
		super(StringAttribute,self).check_value()
		if self.value is not None:
			try:
				assert(len(self.value) == 36)
				assert(all([c in BASE16_ALPHABET for c in self.value.lower()]))
				lens = [len(o) for o in self.value.split('-')]
				assert(lens.count(4) == 3 and set(lens) == {8,4,12})
			except AssertionError: 
				raise AttributeValueException("Wrong str format for UUID4Attribute")

	def generate_random_value():
		return str(uuid.uuid4())


class UTF8BASE64Attribute(StringAttribute):
	"""docstring for UTF8BASE64Attribute"""
	def __init__(self, *args, **kwargs):
		kwargs['force_cast'] = kwargs.get('force_cast',lambda x:UTF8BASE64Attribute.decode(x))
		super(UTF8BASE64Attribute, self).__init__(*args, **kwargs)
		self.check_value()

	def decode(x):
		try:
			return base64.b64decode(x).decode('utf-8')
		except:
			return x
		

class IntegerAttribute(Attribute):
	"""docstring for IntegerAttribute"""
	def __init__(self, name, **kwargs):
		super(IntegerAttribute, self).__init__(name,int,**kwargs)
		self.check_value()

class RealAttribute(Attribute):
	"""docstring for RealAttribute"""
	def __init__(self, name, **kwargs):
		kwargs['force_cast'] = kwargs.get('force_cast',float)
		super(RealAttribute, self).__init__(name,float,**kwargs)
		self.check_value()

class BooleanAttribute(Attribute):
	"""docstring for BooleanAttribute"""
	def __init__(self, name, **kwargs):
		kwargs['force_cast'] = kwargs.get('force_cast',bool)
		super(BooleanAttribute, self).__init__(name,bool,**kwargs)
		self.check_value()

class DateAttribute(Attribute):
	"""docstring for DateAttribute"""
	def __init__(self, name, **kwargs):
		super(DateAttribute, self).__init__(name,date,**kwargs)
		self.check_value()

class DateTimeAttribute(Attribute):
	"""docstring for DateTimeAttribute"""
	def __init__(self, name, **kwargs):
		super(DateTimeAttribute, self).__init__(name,datetime,**kwargs)
		self.check_value()