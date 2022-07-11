
import sys, asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
from typing import List



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


#Добаление элемента в базу
async def add(engine, person: dict) -> str:
    async with engine.acquire() as conn:
        await conn.execute(users.insert().values(first_name=person['first_name'], last_name=person['last_name']))
        id = 0
        async for row in conn.execute(users.select().where(users.c.first_name == person['first_name'])):
            if row.id > id:
                id = row.id
        return id




#Удаление элемента из базы
async def delete(engine, id: str):
    async with engine.acquire() as conn:
        await conn.execute(sa.delete(users).where(users.c.id == int(id)))


#Изменение элемента
async def set(engine, person: dict):
     async with engine.acquire() as conn:
         await conn.execute(sa.update(users).values({'first_name': person['first_name'], "last_name": person['last_name']}).where((users.c.id == person['id'])))



# Получение элемента
async def get(engine, id: str) -> dict:
    async with engine.acquire() as conn:
        async for row in conn.execute(users.select().where(users.c.id == int(id))):
            print(row.id, row.first_name, row.last_name)
            return {'id': row.id, 'first_name': row.first_name, 'last_name': row.last_name}


#Список пользователей по фильтру
async def get_list(engine, filter: dict, order: List[dict], limit: int, offset: int) -> List[dict]:
    async with engine.acquire() as conn:
        list_lname = []
        #Фильтр по фамилии
        if 'values' in filter['last_name']:

            for i in filter['last_name']['values']:
                async for row in conn.execute(users.select().where(i == users.c.last_name)):
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name' : row.last_name})
                    #print(row.id, row.first_name, row.last_name)

        elif 'like' in filter['last_name']:
            like = filter['last_name']['like']
            async for row in conn.execute(users.select()):
                if like in row.last_name:
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name' : row.last_name})
                    #print(row.id, row.first_name, row.last_name)
        elif 'ilike' in filter['last_name']:
            ilike = filter['last_name']['ilike']
            async for row in conn.execute(users.select()):
                if ilike.lower() in row.last_name.lower():
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name' : row.last_name})
                    #print(row.id, row.first_name, row.last_name)

        # Фильтр для имени
        list_fname = []
        if 'values' in filter['first_name']:
            for i in filter['first_name']['values']:
                for j in range(len(list_lname)):
                    if i == list_lname[j]['first_name']:
                        list_fname.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'], 'last_name' : list_lname[j]['last_name']})
                        #print(list_lname[j]['id'], list_lname[j]['first_name'],  list_lname[j]['last_name'])

        elif 'like' in filter['first_name']:
            like = filter['first_name']['like']
            for j in range(len(list_lname)):
                if like in list_lname[j]['first_name']:
                    list_fname.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'], 'last_name': list_lname[j]['last_name']})
                    #print(list_lname[j]['id'], list_lname[j]['first_name'], list_lname[j]['last_name'])

        elif 'ilike' in filter['first_name']:
            ilike = filter['first_name']['ilike']
            for j in range(len(list_lname)):
                if ilike.lower() in list_lname[j]['first_name'].lower():
                    list_fname.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                 'last_name': list_lname[j]['last_name']})
                    #print(list_lname[j]['id'], list_lname[j]['first_name'], list_lname[j]['last_name'])

    #Сортировка
    if order[0]['direction'] == 'asc':
        list_fname.sort(key=lambda d: d[order[0]['field']])
    else:
        list_fname.sort(key=lambda d: d[order[0]['field']], reverse=True)

    #Ограничения количества
    list = []
    if offset < len(list_fname):
        for i in range(offset, len(list_fname)):
            list.append(list_fname[i])

    if len(list) > limit:
        edge = limit
        for i in range((limit), (len(list))):
            list.pop(edge)


    for i in range(len(list)):
        print(list[i]['id'], list[i]['first_name'], list[i]['last_name'])
    return list



async def get_count(engine, filter: dict) -> int:
    async with engine.acquire() as conn:
        list_lname = []
        temp_dist = {'id': '', 'first_name': '', 'last_name' : ''}
        if 'values' in filter['last_name']:
            limit_iter=0
            offset_iter = 1
            for i in filter['last_name']['values']:
                async for row in conn.execute(users.select().where(i == users.c.last_name)):
                    list_lname.append({'id': row.id, 'first_name': row.first_name, 'last_name' : row.last_name})
                    #print(row.id, row.first_name, row.last_name)
        elif 'like' in filter['last_name']:
            like = filter['last_name']['like']
            async for row in conn.execute(users.select()):
                if like in row.last_name:
                    list_lname.append(temp_dist)
                    #print(row.id, row.first_name, row.last_name)
        elif 'ilike' in filter['last_name']:
            ilike = filter['last_name']['ilike']
            async for row in conn.execute(users.select()):
                if ilike.lower() in row.last_name.lower():
                    list_lname.append(temp_dist)
                    #print(row.id, row.first_name, row.last_name)

        # Фильтр для имени
        list = []
        if 'values' in filter['first_name']:
            for i in filter['first_name']['values']:
                for j in range(len(list_lname)):
                    if i == list_lname[j]['first_name']:
                        list.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'], 'last_name' : list_lname[j]['last_name']})
                        #print(list_lname[j]['id'], list_lname[j]['first_name'],  list_lname[j]['last_name'])

        elif 'like' in filter['first_name']:
            like = filter['first_name']['like']
            for j in range(len(list_lname)):
                if like in list_lname[j]['first_name']:
                    list.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'], 'last_name': list_lname[j]['last_name']})
                    #print(list_lname[j]['id'], list_lname[j]['first_name'], list_lname[j]['last_name'])

        elif 'ilike' in filter['first_name']:
            ilike = filter['first_name']['ilike']
            for j in range(len(list_lname)):
                if ilike.lower() in list_lname[j]['first_name'].lower():
                    list.append({'id': list_lname[j]['id'], 'first_name': list_lname[j]['first_name'],
                                 'last_name': list_lname[j]['last_name']})
                    #print(list_lname[j]['id'], list_lname[j]['first_name'], list_lname[j]['last_name'])
    for i in range(len(list)):
        print(list[i]['id'], list[i]['first_name'], list[i]['last_name'])
    print(len(list))
    return len(list)


async def get_all(engine):
    async with engine.acquire() as conn:
        res = []
        async for row in conn.execute(users.select()):
            res.append({"id": row.id, "first_name": row.first_name, "last_name": row.last_name})
        return res

async def go():

    async with create_engine(user='postgres',
                             database='people_vladimir',
                             host='127.0.0.1',
                             password='1234'
                             ) as engine:

        #await add(engine, {'first_name': 'Zlata', 'last_name': 'Protivogaz'})
        #await set(engine, {'id': 3, 'first_name': 'Jorno', 'last_name': 'Jorvano'})
        #await  delete(engine, 2)
        #await get(engine, '3')
        #await get_list(engine, {"first_name": {"ilike": "a"}, "last_name": {"ilike": "A"}}, [{"field": "id", "direction": "asc or desc"}], 10, 0)
        await get_list(engine, {"first_name": {"ilike": 'a'}, "last_name": {"ilike": 'a'}}, [{'field': 'id', 'direction': 'asc'}], 20, 1)
        #await get_count(engine, {"first_name": {"ilike": 'r'}, "last_name": {"values": ['Protivogaz']}})

loop = asyncio.get_event_loop()
loop.run_until_complete(go())




'''
import psycopg2
import sys
import aiopg
import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
import asyncio
from aiopg.sa import create_engine
import sqlalchemy as sa
try:
    connection = psycopg2.connect(
        host='127.0.0.1',
    #    host = '192.168.1.245',
        user='postgres',
        password='1234',
        database='people_vladimir'

    )
    connection.autocommit = True


    #cursor = connection.cursor()

    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")

        print(f"Server version: {cursor.fetchone()}")

    #Создание новой таблицы

    
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE users(
            id serial PRIMARY KEY,
            first_name varchar(50) NOT NULL,
            last_name varchar(50) NOT NULL);"""
        )
        #connection.commit()
        print("[INFO] Table created succesfilly")



    #Ввод данных в таблицу
  
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO users (first_name, last_name) VALUES
            ('0leg', 'Olegov'),
            ('Kirill', 'Zhokov'),
            ('Vladimir', 'Lavrukhin')"""
        )
    print("[INFO] Data was succefully unserted")
 

    #Извлечение данных из таблицы

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT first_name, last_name FROM users;"""
        )
        print(cursor.fetchone())



except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("[INFO] PostgreSQL connection closed")


'''

