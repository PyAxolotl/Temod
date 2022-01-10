import ntpath
import os

class DirectoryStorageException(Exception):
	"""docstring for DirectoryStorageException"""
	def __init__(self, *args, **kwargs):
		super(DirectoryStorageException, self).__init__(*args, **kwargs)

class DirectoryStorage(object):
	"""docstring for DirectoryStorage"""
	def __init__(self, directory, mode="b", encoding="utf-8",createDir=False):
		super(DirectoryStorage, self).__init__()
		try:
			assert(os.path.isdir(directory))
		except AssertionError:
			if not createDir:
				raise DirectoryStorageException(f"{directory} does not exist.")
			os.mkdir(directory)
		self.directory = directory
		self.name = ntpath.basename(directory)
		self.mode = mode
		self.encoding = encoding

	def subStorage(self, dirname, createDir=False,mode=None):
		mode = self.mode if mode is None else mode
		return DirectoryStorage(os.path.join(self.directory,dirname),mode=mode,createDir=createDir)

	def subStorages(self,mode=None):
		mode = self.mode if mode is None else mode
		for dirname in os.listdir(self.directory):
			path = os.path.join(self.directory,dirname)
			if os.path.isdir(path):
				yield DirectoryStorage(path,mode=self.mode,createDir=False)

	def content(self,only_files=False):
		for file in os.listdir(self.directory):
			path = os.path.join(self.directory,file)
			if not only_files or os.path.isfile(path):
				yield file

	def has(self,file):
		return file in os.listdir(self.directory)

	def rename(self,old,new):
		os.rename(os.path.join(self.directory,old),os.path.join(self.directory,new))

	def read(self,file,mode=None,encoding=None):
		mode = self.mode if mode is None else mode
		encoding = self.encoding if encoding is None else encoding
		try:
			with open(os.path.join(self.directory,file),"r"+mode,encoding=encoding) as stream:
				content = stream.read()
			return content
		except FileNotFoundError:
			pass

	def delete(self,file,strict=False):
		try:
			os.remove(os.path.join(self.directory,file))
			return file
		except FileNotFoundError as e:
			if strict:
				raise e

	def write(self,file,content,mode=None,encoding=None):
		encoding = self.encoding if encoding is None else encoding
		mode = self.mode if mode is None else mode
		with open(os.path.join(self.directory,file),"w"+mode,encoding=encoding) as stream:
			stream.write(content)

	def close(self):
		pass