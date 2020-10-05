from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import db_map as db
from settings import config
from lexicon import separator

engine = create_engine(f'sqlite:///../{config.database.name}', echo=False)
db.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class AttrDict(dict):
    """Let to get access to dictionary keys through dot"""

    def __getattr__(self, name):
        return self[name]


def row_to_dict(row):
    """Creates a dictionary from db answer"""
    dictionary = {}
    for column in row.__table__.columns:
        dictionary[column.name] = str(getattr(row, column.name))
    return AttrDict(dictionary)


class User(db.User):
    @staticmethod
    def get(message):
        session = Session()
        try:
            user = row_to_dict(session.query(User).filter(
                User.id == message.from_user.id).one())
        except Exception as e:
            print(e)
            return False
        else:
            return user
        finally:
            session.close()

    @staticmethod
    def add(message):
        session = Session()
        try:
            user = User(message.from_user.id, message.from_user.first_name,
                        message.from_user.last_name, message.date)
        except Exception as e:
            print(e)
            return False
        else:
            session.add(user)
            session.commit()
            return True
        finally:
            session.close()


class Chat(db.Chat):
    @staticmethod
    def get(message):
        session = Session()
        try:
            chat = row_to_dict(session.query(Chat).filter(
                Chat.id == message.chat.id).one())
        except Exception as e:
            print(e)
            return False
        else:
            return chat
        finally:
            session.close()

    @staticmethod
    def add(message):
        session = Session()
        try:
            chat = Chat(message.chat.id, message.date, float(message.text))
        except Exception as e:
            print(e)
            return False
        else:
            session.add(chat)
            session.commit()
            return True
        finally:
            session.close()

    @staticmethod
    def set(message):
        session = Session()
        try:
            chat = session.query(Chat).filter(
                Chat.id == message.chat.id).one()
            if chat.memory is None:
                memory = message.text
            else:
                memory = chat.memory + separator + message.text
            session.query(Chat).filter(
                Chat.id == message.chat.id).update({"memory": memory})
        except Exception as e:
            print(e)
            return False
        else:
            session.commit()
        finally:
            session.close()

    @staticmethod
    def reset(message):
        session = Session()
        try:
            session.query(Chat).filter(
                Chat.id == message.chat.id).update({"memory": None})
        except Exception as e:
            print(e)
            return False
        else:
            session.commit()
        finally:
            session.close()


class Category(db.Category):
    @staticmethod
    def get(message):
        session = Session()
        try:
            session.query(Category).filter(
                Category.name == message.text,
                Category.chat == message.chat.id).one()
        except Exception as e:
            print(e)
            return False
        else:
            return True
        finally:
            session.close()

    @staticmethod
    def get_all(message):
        session = Session()
        try:
            memory = Chat.get(message).memory.split(separator)
            category_rows = session.query(
                Category).filter(Category.chat == message.chat.id,
                                 Category.command == memory[0],
                                 Category.parent.is_(None))
            categories = []
            for category_row in category_rows:
                categories.append(category_row.name)
        except Exception as e:
            print(e)
            return False
        else:
            return categories
        finally:
            session.close()

    @staticmethod
    def get_subcategories(message):
        session = Session()
        try:
            memory = Chat.get(message).memory.split(separator)
            category_rows = session.query(
                Category).filter(Category.chat == message.chat.id,
                                 Category.command == memory[0],
                                 Category.parent == memory[1])
            categories = []
            for category_row in category_rows:
                categories.append(category_row.name)
        except Exception as e:
            print(e)
            return False
        else:
            return categories
        finally:
            session.close()

    @staticmethod
    def add(message):
        session = Session()
        if not Category.get(message):
            try:
                memory = Chat.get(message).memory.split(separator)
                if len(memory) == 3:
                    parent = memory[1]
                else:
                    parent = None
                category = Category(message.chat.id, memory[0], parent,
                                    message.text)
            except Exception as e:
                print(e)
                return False
            else:
                session.add(category)
                session.commit()
                return True
            finally:
                session.close()


class Transaction(db.Transaction):
    @staticmethod
    def add(message):
        session = Session()
        try:
            memory = Chat.get(message).memory.split(separator)
            date = datetime.utcfromtimestamp(message.date)
            year = date.strftime('%Y')
            month = date.strftime('%m')
            day = date.strftime('%d')
            time = date.strftime('%H:%M')
            if len(memory) == 3:
                subcategory = memory[2]
            else:
                subcategory = None
            transaction = Transaction(message.chat.id, message.from_user.id,
                                      memory[0], memory[1], subcategory,
                                      year, month, day, time,
                                      float(message.text))
            chat = Chat.get(message)
            if memory[0] == 'Доход':
                balance = round(float(chat.balance) + float(message.text), 2)
            else:
                balance = round(float(chat.balance) - float(message.text), 2)
            session.query(Chat).filter(
                Chat.id == message.chat.id).update({"balance": balance})
        except Exception as e:
            print(e)
            return False
        else:
            session.add(transaction)
            session.commit()
            return True
        finally:
            session.close()

    @staticmethod
    def get_years(message):
        session = Session()
        try:
            years_row = session.query(Transaction.year.distinct()).filter(
                Transaction.chat == message.chat.id).all()
            years = []
            for year in years_row:
                years.append(str(year[0]))
        except Exception as e:
            print(e)
            return False
        else:
            return years
        finally:
            session.close()

    @staticmethod
    def get_months(message):
        session = Session()
        try:
            year = Chat.get(message).memory.split(separator)[1]
            months_row = session.query(
                Transaction.month.distinct()).filter(
                Transaction.chat == message.chat.id,
                Transaction.year == year).all()
            months = []
            for month in months_row:
                months.append(str(month[0]))
        except Exception as e:
            print(e)
            return False
        else:
            return months
        finally:
            session.close()

    @staticmethod
    def get_report(message):
        session = Session()
        try:
            memory = Chat.get(message).memory.split(separator)
            transactions = session.query(Transaction).filter(
                Transaction.chat == message.chat.id,
                Transaction.year == memory[1],
                Transaction.month == memory[2]).all()
        except Exception as e:
            print(e)
            return False
        else:
            report = {}
            for transaction in transactions:
                name = transaction.name
                if name in report:
                    report[name] += transaction.value
                else:
                    report[name] = transaction.value
            result = ''
            for key, value in sorted(report.items()):
                result += f'\n{key}: {value}'
        finally:
            session.close()
