from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, relationship, session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()

class User_on_questions():
    questions: list
    user_id: int

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    stage = Column(Integer)
    def __init__(self):
        self.id = None
        self.stage = None

    def set_id(self, _id):
        self.id = _id

    def set_stage(self, _stage):
        self.stage = _stage

    def get_id(self):
        return self.id

    def get_stage(self):
        return self.stage

class Questions(Base):
    __tablename__ = 'Questions'
    id = Column(Integer, primary_key=True)
    question = Column(String)

    def __init__(self):
        self.id = None
        self.question = None

    def set_question(self, _question):
        self.question = _question

    def get_question(self):
        return self.question

    def set_id(self, _id):
        self.id = _id

    def get_id(self):
        return self.id


class Answers(Base):
    __tablename__ = 'Answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship('User', backref='Answers')
    Question_number = Column(Integer)
    Answer = Column(String)

    def __init__(self):
        self.Question_number = None
        self.Answer = None

    def set_Question_number(self, _question_number):
        self.Question_number = _question_number

    def set_Answer(self, _answer):
        self.Answer = _answer

    def set_User_id(self, _user_id):
        self.user_id = _user_id

    def get_Question_number(self):
        return self.Question_number

    def get_Answer(self):
        return self.Answer

    def get_User_id(self):
        return self.user_id


class Interaction_DB():
    session: session

    def __init__(self, _session):
        self.session = _session

    def set_some_questions(self, dict_of_questions):
        try:
            index = 0
            for key in dict_of_questions:
                new_question = Questions()
                new_question.set_id(key)
                new_question.set_question(dict_of_questions[key])
                self.session.add(new_question)
                self.session.commit()
                index += 1
            new_question = Questions()
            new_question.set_id(index + 1)
            new_question.set_question('Зарплатные ожидания')
            self.session.add(new_question)
            self.session.commit()
        except:
            print('')


    def add_new_user(self, user_id, _stage):
        new_user = User()
        new_user.set_id(user_id)
        new_user.set_stage(_stage)
        self.session.add(new_user)
        self.session.commit()

    def check_user_id(self, user_id) -> bool:
        try:
            user = self.session.query(User).filter_by(id=user_id).one()
            return True
        except (InvalidRequestError, NoResultFound):
            return False

    def replace_user_stage(self, user_id, _stage):
        self.session.query(User).filter_by(id=user_id).update({'stage': _stage})
        self.session.commit()

    def return_user_by_id(self, user_id):
        user = self.session.query(User).filter_by(id=user_id).one()
        return user

    def check_user_stage(self, user_id, _stage):
        user = self.session.query(User).get(user_id)
        print(user.get_stage())
        print(_stage)
        if _stage == user.get_stage():
            return True
        else:
            return False

    def add_answer(self, user_id, _answer, _question_id):
        answer = Answers()
        answer.set_Question_number(_question_id)
        answer.set_User_id(user_id)
        answer.set_Answer(_answer)
        self.session.add(answer)
        self.session.commit()

    def get_answer_count(self, user_id):
        count = self.session.query(Answers).filter_by(user_id=user_id).count()
        return count

    def get_question_by_id(self, question_id):
        question = self.session.query(Questions).filter_by(id=question_id).one()
        return question.question

    def add_salary(self, user_id, _answer):
        answer = Answers()
        answer.set_Question_number(3)
        answer.set_User_id(user_id)
        answer.set_Answer(_answer)
        self.session.add(answer)
        self.session.commit()

    def delete_user_answers(self, user_id):
        self.session.query(Answers).filter_by(user_id=user_id).delete()
        self.session.commit()

def connect_to_DB():
    engine = create_engine('sqlite:///sqlite3.db')
    Base.metadata.create_all(engine)
    return engine

