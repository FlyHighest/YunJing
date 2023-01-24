import sys
sys.path.append("..")
from peewee import Model,CharField, MySQLDatabase,DateTimeField,IntegerField,AutoField,ForeignKeyField,BooleanField,TextField
from secret import mysql_db_database,mysql_db_host,mysql_db_password,mysql_db_user
import datetime

mysql_db = MySQLDatabase(
    host=mysql_db_host,
    user=mysql_db_user,
    password=mysql_db_password,
    database=mysql_db_database,
    thread_safe=True
)

class BaseModel(Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db

class User(BaseModel):
    userid = AutoField() # primary key
    username = CharField(unique=True)
    password = CharField()
    jointime = DateTimeField(default=datetime.datetime.now)
    email = CharField()
    phone = CharField()
    level = IntegerField() 



class Image(BaseModel):
    genid = CharField(unique=True,primary_key=True)
    imgurl = CharField()
    numlikes = IntegerField(default=0)
    params = TextField()
    modelname=CharField()
    prompt=TextField()
    published = BooleanField()
    gentime = DateTimeField(default=datetime.datetime.now)
    userid = ForeignKeyField(model=User,backref="images")
    height = IntegerField()
    width  = IntegerField()

class Likes(BaseModel):
    userid = ForeignKeyField(model=User,backref="user_likes")
    genid = ForeignKeyField(model=Image, backref="genid_liked_by_users")

    class Meta:
        # `indexes` is a tuple of 2-tuples, where the 2-tuples are
        # a tuple of column names to index and a boolean indicating
        # whether the index is unique or not.
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('userid', 'genid'), True),
        )

class Histories(BaseModel):
    userid =  ForeignKeyField(model=User,backref="user_history")
    imgurl = CharField()
    gentime = DateTimeField(default=datetime.datetime.now)

if __name__=="__main__":
    mysql_db.connect()
    mysql_db.create_tables([User,Image,Likes,Histories])
    mysql_db.execute_sql("CREATE FULLTEXT INDEX ft_index ON Image (prompt) WITH PARSER ngram")
    import nanoid
    print(User.create(username="匿名用户",password=nanoid.generate(size=30)))
    mysql_db.close()
