import logging

from typing import Type

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Session

from . import Base

MAX_BUTTONS = 4
logger = logging.getLogger('livetrenibot')

class User(Base):
    __tablename__ = 'users'
    chat_id = Column(Integer, primary_key=True)
    buttons = relationship('Button', back_populates='user', order_by='Button.position', cascade="all, delete-orphan")

    @staticmethod
    def get_user(session: Session, chat_id: int) -> 'User':
        user = session.query(User).filter_by(chat_id=chat_id).first()
        if not user:
            user = User(chat_id=chat_id)
            session.add(user)
            session.commit()
        return user

    def insert_button(self, session: Session, label):
        buttons = session.query(Button).filter(Button.chat_id == self.chat_id)

        # if the button already exists, move it into pos 0
        if button := buttons.filter(Button.label == label).first():
            logger.debug(f'Button {button.label} already exists at position {button.position}')
            buttons.filter(Button.position < button.position).update({Button.position: Button.position + 1})
            button.position = 0
        else:
            buttons.filter(Button.position >= MAX_BUTTONS - 1).delete(synchronize_session='fetch')
            buttons.update({Button.position: Button.position + 1})
            new_button = Button(chat_id=self.chat_id, label=label, position=0)
            session.add(new_button)

        session.commit()


class Button(Base):
    __tablename__ = 'buttons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('users.chat_id', ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    user = relationship('User', back_populates='buttons')

engine = create_engine("sqlite:///sqlite.db")
SessionFactory = sessionmaker(bind=engine)