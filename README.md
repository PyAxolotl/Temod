# Temod
Temod is a python library designed to augment the portability of python program using database. From now on, this package will be maintained here [https://github.com/TuburboMajus/temod](https://github.com/TuburboMajus/temod).

## Intro
Temod adds a new layer of abstraction to your programs in which common databases' notions are defined such as:
* Attributes: Typed attributes like Integers, Strings, ... 
* Entities
* Relations
* Conditions
* ...

This implementation help to build your program's data structures without regard of the database your using or intend to use.

## Portability
Once your data structures defined (Entities, Attributes, ...), you can chose the right storage for your database to translate this structure
to the specific language of your chosen database.

For now, there is only the mysql translator but more translators like neo4j or mongodb are planned to be added.

### Mysql Translation
The Mysql Translator does the following matching:
- Entity -> Table
- Attribute -> Column
- Relation -> Constraint
- Join -> Table Join

## Hello Temod
Let's say that we have a program that analyses and stores press articles.
For the sake of the example, let's say that we divide the article object in two parts:
* The headers: contains the title, the source and the publish date of the article
* The corpus: contains the content of the article.

### The entities
We start by building our two entities:
```python
class ArticleHeader(Entity): # temod.core.base.entity.Entity
  ENTITY_NAME = 'articleHeader'
  ATTRIBUTES = ["id","title","source","publishDate"]
  def __init__(self,id,title,source,publishDate=None): # Let's suppose that we can't retrieve the publish date of some articles
    super(ArticleHeader,self).__init__(
      IntegerAttribute("id",value=id,is_id=True,is_nullable=False,is_auto=True), 
      StringAttribute("title",value=title,is_nullable=False,non_empty=True),
      StringAttribute("source",value=source,is_nullable=False,non_empty=True),
      DateAttribute("publishDate",value=title)
    )
    
class ArticleCorpus(Entity):
  ENTITY_NAME = 'articleCorpus'
  ATTRIBUTES = ["id","content"]
  def __init__(self,id,content):
    super(ArticleHeader,self).__init__(
      IntegerAttribute("id",value=id,is_id=True,is_nullable=False,is_auto=True), 
      StringAttribute("content",value=content,is_nullable=False,non_empty=True)
    )
```

You can access any attribute of the entity by simply accessing entity.attribute_name
But to set its value you must use the setAttribute method
```python
a = ArticleHeader(1,"Hello Temod","Github"); print(a.id) # prints 1
a.setAttribute("title","New title"); print(a.title) # prints "New title"
```

### Storing my entities
Since only the mysql database handler has been implemented for now, we will use it in our example.
To implement a handler that will take care of listing, updating, deleting, counting, ... our objects build a
class that inherits from the MysqlEntityStorage (temod.storages.base.mysqlEntityStorage) like so:
```python
class MysqlArticleHeaderStorage(MysqlEntityStorage):
  def __init__(self,**kwargs):
    super(MysqlArticleHeaderStorage,self).__init__(ArticleHeader,**kwargs)
```

With simply this class, you can now store ArticleHeader objects into your database.
The database credentials are passed into "kwargs" (user, password, host, port, database).
This class will take care automatically care of formatting the attributes when storing them
and can list, update, delete from you database.

The MysqlArticleHeaderStorage will store our ArticleHeader objects into the table "articleHeader" or any
other value specified in the ENTITY_NAME propery of ArticleHeader

```python
storage = MysqlArticleHeaderStorage(user="me",password="this temod version uses plain text password authentification.. i think",database="articles")

new_object_id = storage.create(ArticleHeader(-1,"First article","Github",date=date.today()))
# The value we give to id won't matter since it has been set to auto increment (is_auto=True) as long as it isn't a null value

article = storage.get(IntegerAttribute("id",value=new_object_id)) # Return the newly stored article
article.takeSnapshot() # Saves the actual attributes' values of the object 
article.setAttribute("title","Modified article")
storage.updateOnSnapshot(article) # Compares the actual state of the object with the snapshot taken earlier and updates only the attributes that has been modified
```

## Contact
If you have any remark or bug reports about Temod you can contact me at:
AbdellatifZied.saada@gmail.com
