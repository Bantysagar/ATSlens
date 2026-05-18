import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DB_FOLDER = Path.home() / ".atslens_data"
DB_FOLDER.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{(DB_FOLDER / 'atslens.db').as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    candidate_type = Column(String(50), nullable=False)
    target_field = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    grade = Column(String(20), nullable=False)
    verdict = Column(String(100), nullable=False)
    mnc_chance = Column(Float, nullable=False)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created.")


def save_analysis(result: dict) -> int:
    db = SessionLocal()

    try:
        record = AnalysisRecord(
            filename=result["filename"],
            candidate_type=result["candidate_type"],
            target_field=result["target_field"],
            score=result["score"],
            grade=result["grade"],
            verdict=result["verdict"],
            mnc_chance=result["mnc_chance"],
            result_json=json.dumps(result)
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record.id

    finally:
        db.close()


def get_analysis(analysis_id: int):
    db = SessionLocal()

    try:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()

        if not record:
            return None

        result = json.loads(record.result_json)
        result["analysis_id"] = record.id
        result["created_at"] = record.created_at.strftime("%d %b %Y")

        return result

    finally:
        db.close()