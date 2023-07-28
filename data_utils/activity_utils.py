# coding=utf-8

import datetime
import typing

import requests
import sqlalchemy
from requests import adapters
from sqlalchemy import orm
from sqlalchemy.dialects import sqlite
from urllib3.util import retry

import entity

# TODO: activity_utils.py 和 product_utils.py 都需要用到这部分 retry 相关的代码
#  是不是整个项目运行一次就行了？可能并不需要在两个文件里都写一遍
retry_strategy = retry.Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = adapters.HTTPAdapter(max_retries=retry_strategy)
requests_session = requests.Session()
requests_session.mount('https://', adapter)

live_id_to_room = {
    1: '李佳琦直播间',
    2: '所有女生直播间',
    3: '所有女生的衣橱',
}
engine = sqlalchemy.create_engine('sqlite:///database.sqlite', echo=True)


def save_activities(activities: typing.List[dict]) -> None:
    sql_session = orm.Session(engine)
    for activity in activities:
        insert_statement = sqlite.insert(entity.Activity).values(activity)
        do_update_statement = insert_statement.on_conflict_do_update(
            index_elements=['id'],
            set_=entity.Activity.get_on_conflict_do_update_set(insert_statement)
        )
        sql_session.execute(do_update_statement)
        sql_session.commit()


def get_activities() -> typing.List[dict]:
    response = requests.get('https://7.meionetech.com/api/live/wx/strategy/activities')
    data = response.json()['data']
    return [__parse_activity(activity) for activity in data]


def __parse_activity(raw_activity: dict) -> dict:
    activity_id = raw_activity['id']
    theme = raw_activity['caTheme'].strip()
    start_time = datetime.datetime.fromisoformat(raw_activity['startLiveTime'])
    end_time = datetime.datetime.fromisoformat(raw_activity['endLiveTime'])
    room = live_id_to_room[raw_activity['liveId']]
    if raw_activity['tag'] != room and raw_activity['tag'] != theme:
        # tag 有时候跟直播间名字相同，有时候跟主题相同，有时候是更完整的主题
        print(raw_activity['tag'], room, theme)
        theme = raw_activity['tag']
    return {
        'id': activity_id,
        'room': room,
        'theme': theme,
        'start_time': start_time,
        'end_time': end_time,
    }


acts = get_activities()
save_activities(acts)
