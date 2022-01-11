from Temod.core.base.condition import *
from .mysqlAttributesTranslator import MysqlAttributesTranslator


class MysqlConditionException(Exception):
	"""docstring for MysqlConditionException"""
	def __init__(self, *args, **kwargs):
		super(MysqlConditionException, self).__init__(*args, **kwargs)


class MysqlConditionsTranslator(object):
	"""docstring for MysqlConditionsTranslator"""
	def __init__(self):
		super(MysqlConditionsTranslator, self).__init__()
		self.attr_translator = MysqlAttributesTranslator()

	def translate_field(self,attribute):
		if attribute.owner_name is None:
			return attribute.name
		return f"{attribute.owner_name}.{attribute.name}"

	def translate(self,condition):
		print(condition)
		if type(condition) is And:
			return self.translate_and(condition)
		if type(condition) is Or:
			return self.translate_or(condition)
		elif type(condition) is Equals:
			return self.translate_equals(condition)
		if type(condition) is StartsWith:
			return self.translate_startswith(condition)
		elif type(condition) is In:
			return self.translate_in(condition)
		else:
			raise MysqlConditionException(f"Can't translate condition of type {type(attribute).__name__}")

	def translate_and(self,condition):
		return " and ".join(["("+self.translate(sub_condition)+")" for sub_condition in condition.conditions])

	def translate_or(self,condition):
		return " or ".join(["("+self.translate(sub_condition)+")" for sub_condition in condition.conditions])

	def translate_startswith(self,condition):
		if condition.case_sensitive:
			condition.field.value = condition.field.value+"%"
			return f"{self.translate_field(condition.field)} LIKE {self.attr_translator.translate(condition.field)}"
		else:
			condition.field.value = condition.field.value.lower()+"%"
			return f"lower({self.translate_field(condition.field)}) LIKE {self.attr_translator.translate(condition.field)}"

	def translate_equals(self,condition):
		if condition.field2 is None:
			return f'{self.translate_field(condition.field1)} = {self.attr_translator.translate(condition.field1)}'
		return f"{self.translate_field(condition.field1)} = {self.translate_field(condition.field2)}"

	def translate_in(self,condition):
		return f"{self.translate_field(condition.field)} in ({','.join([self.attr_translator.translate(attr) for attr in condition.values])})"
		