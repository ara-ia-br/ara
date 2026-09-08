from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session

from app.security.settings import setting


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=setting.DB_USER,
    password=setting.DB_PASSWORD,
    host=setting.DB_HOST,
    port=setting.DB_PORT,
    database=setting.DB_NAME,
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()