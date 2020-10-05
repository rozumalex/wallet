from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    created = Column(Integer)

    def __init__(self, id, first_name, last_name, created):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.created = created


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    created = Column(Integer)
    balance = Column(Float)
    memory = Column(String)

    def __init__(self, id, created, balance):
        self.id = id
        self.created = created
        self.balance = balance


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    chat = Column(Integer)
    command = Column(String)
    parent = Column(String)
    name = Column(String)

    __table_args__ = (UniqueConstraint('chat', 'name', name='_chat_name_uni'),)

    def __init__(self, chat, command, parent, name):
        self.chat = chat
        self.command = command
        self.parent = parent
        self.name = name


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    chat = Column(Integer, ForeignKey(Chat.id))
    user = Column(Integer, ForeignKey(User.id))
    command = Column(String)
    category = Column(String)
    subcategory = Column(String)
    value = Column(Float)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(String)
    time = Column(String)

    def __init__(self, chat, user, command, category, subcategory,
                 year, month, day, time, value):
        self.chat = chat
        self.user = user
        self.command = command
        self.category = category
        self.subcategory = subcategory
        self.year = year
        self.month = month
        self.day = day
        self.time = time
        self.value = value
