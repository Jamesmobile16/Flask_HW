from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, func

engine = create_engine('postgresql://app:1234@127.0.0.1:5431/app')
Session = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)


class Adv(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    author = Column(String)


Base.metadata.create_all()