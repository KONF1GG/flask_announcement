import datetime
from sqlalchemy import create_engine, String, DateTime, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
import os
import atexit
import dotenv


dotenv.load_dotenv()


POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5431')
POSTGRES_DB = os.getenv('POSTGRES_DB',)

SQLALCHEMY_DSN = 'postgresql://{}:{}@{}:{}/{}'.format(POSTGRES_USER, POSTGRES_PASSWORD,
                                                      POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB)

engine = create_engine(SQLALCHEMY_DSN)

try:
    Session = sessionmaker(bind=engine)
except Exception as e:
    print("Ошибка при создании сессии:", e)

atexit.register(engine.dispose)


class Base(DeclarativeBase):
    pass


class Announcement(Base):
    __tablename__ = 'announcements'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    @property
    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'owner': self.owner,
        }

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Ошибка при создании таблицы:", e)
