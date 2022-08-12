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

	######################################################################

	def subStorage(self, dirname, *args, createDir=False,mode=None,as_=None,**kwargs):
		mode = self.mode if mode is None else mode
		storageType = type(self) if as_ is None else as_
		return storageType(os.path.join(self.directory,dirname),*args,mode=mode,createDir=createDir,**kwargs)

	def subStorages(self,*args,mode=None,as_=None,**kwargs):
		mode = self.mode if mode is None else mode
		storageType = type(self) if as_ is None else as_
		for dirname in os.listdir(self.directory):
			path = os.path.join(self.directory,dirname)
			if os.path.isdir(path):
				yield storageType(path,*args,mode=self.mode,createDir=False,**kwargs)

	######################################################################

	def content(self,only_files=False):
		for file in os.listdir(self.directory):
			path = os.path.join(self.directory,file)
			if not only_files or os.path.isfile(path):
				yield file 

	def has(self,file):
		return file in os.listdir(self.directory)

	######################################################################

	def rename(self,old,new):
		os.rename(os.path.join(self.directory,old),os.path.join(self.directory,new))

	def moveToStorage(self,file,storage):
		if not issubclass(type(storage),DirectoryStorage):
			raise DirectoryStorageException("Can only move to another Directory Storage")
		os.rename(os.path.join(self.directory,old),os.path.join(storage.directory,new))

	def copyToStorage(self,file,storage,mode=None,encoding=None):
		if not issubclass(type(storage),DirectoryStorage):
			raise DirectoryStorageException("Can only copy to another Directory Storage")
		mode = self.mode if mode is None else mode
		encoding = self.encoding if encoding is None else encoding
		storage.write(file,self.read(file,mode=mode,encoding=encoding),mode=mode,encoding=encoding)

	######################################################################

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
		kwargs = {} if mode == "b" else {'encoding':encoding}
		path = os.path.join(self.directory,file)
		with open(path,"w"+mode,**kwargs) as stream:
			stream.write(content)
		return path

	######################################################################

	def close(self):
		pass