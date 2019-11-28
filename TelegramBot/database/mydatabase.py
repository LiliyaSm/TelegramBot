from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func
from sqlalchemy.sql import select
from sqlalchemy.sql import and_, or_, not_

SQLITE = 'sqlite'
# Table Names
USERS = 'users'
LINKS = 'links'


class MyDatabase:
    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.lower()
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            print("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        metadata = MetaData()
        self.users = Table(USERS, metadata,
                      Column('id', Integer, primary_key=True),
                      Column('user_id', Integer),
                      Column('link', String),
                      Column('price', Integer)
                      )
        # links = Table(LINKS, metadata,
        #               Column('id', Integer, primary_key=True),
        #               Column('user_name', String),
        #               Column('price', Integer)
        #               )
        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def execute_query(self, query=''):
        if query == '':
            return
        print(query)
        with self.db_engine.connect() as connection:
            try:
                return connection.execute(query)
            except Exception as e:
                print(e)

    def execute_scalar(self, query=''):
        if query == '':
            return
        print(query)
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query).scalar()
                return result
            except Exception as e:
                print(e)

    def print_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format(table)
        print(query)
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)  # print(row[0], row[1], row[2])
                result.close()
        print("\n")

    def data_insert(self, user_id, link, price):
        # Insert Data
        
        #query = "INSERT INTO USERS (user_id, link, price) VALUES ({},{},{});".format(user_id, link, price)

        query = self.users.insert().values(user_id=user_id, link = link, price = price)
        self.execute_query(query)
        self.print_all_data(USERS)


    def search_count(self, user_id):
        # query = "SELECT COUNT(*) FROM USERS WHERE user_id = {};".format(
            # user_id)
        query = select([func.count()]).where(self.users.c.user_id == user_id)
        count=self.db_engine.connect().execute(query).scalar()
        print(query)
        return count

    def search(self, user_id):
        s=select([self.users.c.id, self.users.c.link]).where(self.users.c.user_id == user_id)
        print(s)
        with self.db_engine.connect() as connection:
            list_of_links={row[0]: row[1] for row in connection.execute(s)}
        print(list_of_links) 
        return list_of_links

    def find_number(self, user_id, link_id):
        print("link_id", link_id)
        print(user_id)
        s=self.users.delete().where(self.users.c.user_id == user_id).where(self.users.c.id == link_id)
        
        print(s)
        result = self.execute_query(s)
        self.print_all_data(USERS)
        print("result.rowcount", result.rowcount)
        if result.rowcount:
            return True
        else:
            return False