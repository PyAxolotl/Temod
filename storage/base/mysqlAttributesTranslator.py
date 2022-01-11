from Temod.core.base.attribute import *

import base64

class MysqlAttributeException(Exception):
	"""docstring for MysqlAttributeException"""
	def __init__(self, *args, **kwargs):
		super(MysqlAttributeException, self).__init__(*args, **kwargs)

class MysqlAttributesTranslator(object):
	"""docstring for MysqlAttributesTranslator"""
	def __init__(self):
		super(MysqlAttributesTranslator, self).__init__()
		self.string_escape = str.maketrans({'"':  r'\"'})

	def translate(self,attribute):
		if attribute.value is None:
			return "null"
		if type(attribute) is StringAttribute:
			return self.translateString(attribute)
		elif type(attribute) is IntegerAttribute:
			return self.translateInteger(attribute)
		elif type(attribute) is RealAttribute:
			return self.translateReal(attribute)
		elif type(attribute) is BooleanAttribute:
			return self.translateBool(attribute)
		elif type(attribute) is DateAttribute:
			return self.translateDate(attribute)
		elif type(attribute) is DateTimeAttribute:
			return self.translateDatetime(attribute)
		elif type(attribute) is UUID4Attribute:
			return self.translateString(attribute)
		elif type(attribute) is UTF8BASE64Attribute:
			return self.translateBase64UTF8(attribute)
		else:
			raise MysqlAttributeException(f"Can't translate attribute of type {type(attribute).__name__}")

	####################################
	# BASIC TRANSLATORS
	####################################

	def translateString(self,attribute):
		return f'"{attribute.value.translate(self.string_escape)}"'

	def translateInteger(self, attribute):
		return str(attribute.value)

	def translateReal(self, attribute):
		return str(attribute.value)

	def translateBool(self,attribute):
		if attribute.value is True:
			return "1"
		elif attribute.value is False:
			return "0"
		raise MysqlAttributeException("Can't translate value {attribute.value} for boolean attribute")

	def translateDate(self,attribute):
		return f'"{attribute.value.strftime("%Y-%m-%d")}"'

	def translateDatetime(self,attribute):
		return f'"{attribute.value.strftime("%Y-%m-%d %H:%M:%S")}"'

	def translateBase64UTF8(self,attribute):
		return f'"{base64.b64encode(attribute.value.encode()).decode("utf-8")}"'

		