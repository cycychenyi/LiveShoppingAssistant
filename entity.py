# coding=utf-8

import dataclasses
import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import sqlite


class Base(orm.DeclarativeBase):
    # 必须写 Base 类，实体类再继承 Base 类，如果实体类直接继承 orm.DeclarativeBase 会报错，具体原因尚未深究
    pass


@dataclasses.dataclass
class Activity(Base):
    __tablename__ = 'activity'

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    room: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String)
    theme: orm.Mapped[str] = orm.mapped_column(sqlalchemy.String)
    start_time: orm.Mapped[datetime.datetime] = orm.mapped_column(sqlalchemy.DateTime)
    end_time: orm.Mapped[datetime.datetime] = orm.mapped_column(sqlalchemy.DateTime)

    @classmethod
    def get_on_conflict_do_update_set(cls, insert_statement: sqlite.Insert):
        return {field: getattr(insert_statement.excluded, field) for field in cls.__dict__['__annotations__'].keys()}


engine = sqlalchemy.create_engine('sqlite:///database.sqlite', echo=True)
Base.metadata.create_all(engine)
