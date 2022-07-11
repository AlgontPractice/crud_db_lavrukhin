import asyncio
import sys
from typing import List

import sqlalchemy as sa

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

metadata = sa.MetaData()

users = sa.Table('users', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('first_name', sa.String(255)),
                 sa.Column('last_name', sa.String(255)))


# Создание таблицы
async def create_table(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXISTS users')
        await conn.execute('''CREATE TABLE users (
                                  id serial PRIMARY KEY,
                                  first_name varchar(255),
                                  last_name varchar(255))''')


# Добавление элемента в базу
async def add(engine, user: dict) -> str:
    async with engine.acquire() as conn:
        await conn.execute(users.insert().values(first_name=user['first_name'], last_name=user['last_name']))
        user_id = 0
        async for row in conn.execute(users.select().where(users.c.first_name == user['first_name'])):
            if row.id > user_id:
                user_id = row.id
        return user_id


# Удаление элемента из базы
async def delete(engine, user_id: str):
    async with engine.acquire() as conn:
        await conn.execute(sa.delete(users).where(users.c.id == int(user_id)))


# Изменение элемента
async def set_user(engine, user: dict):
    async with engine.acquire() as conn:
        await conn.execute(
            sa.update(users).values({'first_name': user['first_name'], "last_name": user['last_name']}).where(
                (users.c.id == user['id'])))


# Получение элемента
async def get(engine, user_id: str) -> dict:
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(users.c.id == int(user_id))):
            return {'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name}


# Список пользователей по фильтру
async def get_list(engine, user_filter: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
    async with engine.acquire() as conn:
        list_lname = []  # Хранение списка, отсортированного от фамилии
        list_fname = []  # Хранение списка, отсортированного от имени

        # Фильтр по фамилии

        # Фильтрация по конкретным значениям (фамилиям)
        if 'values' in user_filter['last_name']:
            for i in user_filter['last_name']['values']:
                async for row in conn.execute(users.select().where(i == users.c.last_name)):
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name})

        # Фильтрация по символам с учетом регистра
        elif 'like' in user_filter['last_name']:
            like = user_filter['last_name']['like']
            async for row in conn.execute(users.select()):
                if like in row.last_name:
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name})

        # Фильтрация по символам без учета регистра
        elif 'ilike' in user_filter['last_name']:
            ilike = user_filter['last_name']['ilike']
            async for row in conn.execute(users.select()):
                if ilike.lower() in row.last_name.lower():
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name})

        # Фильтр для имени
        # Фильтрация по конкретным значениям (Именам)
        if 'values' in user_filter['first_name']:
            for i in user_filter['first_name']['values']:
                for j in range(len(list_lname)):
                    if i == list_lname[j]['first_name']:
                        list_fname.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                           'last_name': list_lname[j]['last_name']})

        # Фильтрация по символам с учетом регистра
        elif 'like' in user_filter['first_name']:
            like = user_filter['first_name']['like']
            for j in range(len(list_lname)):
                if like in list_lname[j]['first_name']:
                    list_fname.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                       'last_name': list_lname[j]['last_name']})

        # Фильтрация по символам без учета регистра
        elif 'ilike' in user_filter['first_name']:
            ilike = user_filter['first_name']['ilike']
            for j in range(len(list_lname)):
                if ilike.lower() in list_lname[j]['first_name'].lower():
                    list_fname.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                       'last_name': list_lname[j]['last_name']})

    # Сортировка
    if order[0]['direction'] == 'asc':
        list_fname.sort(key=lambda d: d[order[0]['field']])
    else:
        list_fname.sort(key=lambda d: d[order[0]['field']], reverse=True)

    # Ограничения количества выводимых элементов
    outcome = []
    if offset < len(list_fname):
        for i in range(offset, len(list_fname)):
            outcome.append(list_fname[i])

    if len(outcome) > limit:
        edge = limit
        for i in range(limit, (len(outcome))):
            outcome.pop(edge)

    return outcome


# Подсчет количества элементов, соответствующих фильтру
async def get_count(engine, user_filter: dict) -> int:
    async with engine.acquire() as conn:
        list_lname = []
        temp_dist = {'id': '', 'first_name': '', 'last_name': ''}

        # Фильтрация по конкретным значениям (фамилиям)
        if 'values' in user_filter['last_name']:
            for i in user_filter['last_name']['values']:
                async for row in conn.execute(users.select().where(i == users.c.last_name)):
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name})

        # Фильтрация по символам с учетом регистра
        elif 'like' in user_filter['last_name']:
            like = user_filter['last_name']['like']
            async for row in conn.execute(users.select()):
                if like in row.last_name:
                    list_lname.append(temp_dist)

        # Фильтрация по символам без учета регистра
        elif 'ilike' in user_filter['last_name']:
            ilike = user_filter['last_name']['ilike']
            async for row in conn.execute(users.select()):
                if ilike.lower() in row.last_name.lower():
                    list_lname.append(temp_dist)

        # Фильтр для имени
        outcome = []

        # Фильтрация по конкретным значениям (Именам)
        if 'values' in user_filter['first_name']:
            for i in user_filter['first_name']['values']:
                for j in range(len(list_lname)):
                    if i == list_lname[j]['first_name']:
                        outcome.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                       'last_name': list_lname[j]['last_name']})

        # Фильтрация по символам с учетом регистра
        elif 'like' in user_filter['first_name']:
            like = user_filter['first_name']['like']
            for j in range(len(list_lname)):
                if like in list_lname[j]['first_name']:
                    outcome.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                    'last_name': list_lname[j]['last_name']})

        # Фильтрация по символам без учета регистра
        elif 'ilike' in user_filter['first_name']:
            ilike = user_filter['first_name']['ilike']
            for j in range(len(list_lname)):
                if ilike.lower() in list_lname[j]['first_name'].lower():
                    outcome.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                    'last_name': list_lname[j]['last_name']})

    return len(outcome)


# Вывод всех пользователей из базы
async def get_all(engine):
    async with engine.acquire() as conn:
        res = []
        async for row in conn.execute(users.select()):
            res.append({"id": row.id, "first_name": row.first_name, "last_name": row.last_name})
        return res

loop = asyncio.get_event_loop()
