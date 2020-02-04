from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func, Boolean
from sqlalchemy.sql import select, and_, or_, not_
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import threading
from parsing import get_price
from handlers import send_alarm
import logging

module_logger = logging.getLogger("botLogger.mydatabase")


DATABASE_URL = 'sqlite:///data.db'
Base = declarative_base()


class Association(Base):
    __tablename__ = 'association'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True) # unique id
    link_id = Column(Integer, ForeignKey('links.id'), primary_key=True)
    created_at = Column(sa.DateTime())

    def __init__(self, created_at=datetime.utcnow()):
        self.created_at = created_at

    user = relationship("User", back_populates="links")
    link = relationship("Link", back_populates="users")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tlg_id = Column(Integer)

    def __init__(self, tlg_id):
        self.tlg_id = tlg_id

    links = relationship(
        "Association",
        back_populates="user")

    def __repr__(self):
        return "<User='%s'>" % (
            self.tlg_id)


class Link(Base):
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    link = Column(String)
    price = Column(Integer)
    archive = Column(Boolean)
    state = Column(Integer)
    updated_at = Column(sa.DateTime())

    def __init__(self, link, price, state, archive=False,  updated_at=datetime.utcnow()):

        self.link = link
        self.price = price
        self.state = state
        self.archive = archive
        self.updated_at = updated_at

    def __repr__(self):
        return "Link({0}, {1}, {2})".format(self.link, self.price, self.updated_at)

    users = relationship(
        "Association",
        back_populates="link")


class MyDatabase:

    # http://docs.sqlalchemy.org/en/latest/core/engines.html

    def __init__(self):
        engine = create_engine(
            DATABASE_URL, echo=True,
            connect_args={'check_same_thread': False})
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Link.metadata.create_all(engine)
        User.metadata.create_all(engine)
        Association.metadata.create_all(engine)

    def data_insert(self, tlg_id, link, price, state):
        # Insert Data
        #query = "INSERT INTO USERS (tlg_id, link, price) VALUES ({},{},{});".format(tlg_id, link, price)
        logger = logging.getLogger("botLogger.mydatabase.data_insert")
        try:
            user = self.session.query(User).filter(
                User.tlg_id == tlg_id).one_or_none()
            if not user:  # create new user
                user = User(tlg_id=tlg_id)
        except Exception as ex:
            logger.exception("there are many users with the same id" + str(ex))
            return False       

        try:       #link seaching 
            link_present = self.session.query(
                Link).filter(Link.link == link).one_or_none() 
        except Exception as ex:  # found many identical links in the database
            #print(ex)
            logger.exception(
                "found many identical links in the database " + str(ex))
            return False
        
        a = Association()
        if not link_present:  # there is no link in the database
            a.link = Link(link=link, price=price, state=state)
        else:  # found one in the database
            belong_to_user = self.session.query(
                Association).join(User).filter(link_present.id == Association.link_id)\
                .filter(User.tlg_id == tlg_id).one_or_none()
            if belong_to_user:
                return False
            else:    
                a.link_id = link_present.id  # there is a link in the database, write only in Association
        user.links.append(a)
        self.session.add(user)
        self.session.commit()
        return True

    def search_count(self, tlg_id):
        # query = "SELECT COUNT(*) FROM USERS WHERE tlg_id = {};".format(tlg_id)
        try:
            

            query = self.session.query(Association).join(User).filter(User.tlg_id == tlg_id)
            count = query.with_entities(func.count(Association.link_id)).scalar()
            
        except Exception as e:
            print(e)
        return count

    def search(self, tlg_id):
        list_of_links = self.session.query(Link).\
        join(Association, User).\
        filter(User.tlg_id == tlg_id)\
            .all() # ищем ссылку по id       

        # select l.url, l.id, l.last_modified
        # from association as u
        # join user as a on u.id == a.user_id
        # join links as l on l.id == a.link_id
        # where  u.tg_id == "SOME_ID"
        
        # s = select([self.users.c.id, self.users.c.link]).where(
        #     self.users.c.tlg_id == tlg_id)

        return list_of_links

    def delete_link(self, tlg_id, link_id=""):
        userId = self.session.query(User.id).filter(
            User.tlg_id == tlg_id).one().id
        if link_id:
            try:       
                rowcount = self.session.query(Association)\
                .filter(Association.link_id == link_id)\
                .filter(Association.user_id == userId)\
                .delete()                
                if(self.session.query(Association).filter(Association.link_id == link_id).count() == 0): # no associations for this link
                    self.session.query(Link).filter(\
                        Link.id == link_id).delete()
                self.session.commit()
                return rowcount
            except Exception as e:
                print(e)
            # s = self.users.delete().where(self.users.c.tlg_id ==
            #                               tlg_id).where(self.users.c.id == link_id)
        else:
            try:
                goods = self.session.query(Link)\
                .join(Association, User)\
                .filter(User.tlg_id == tlg_id).all()
                for row in goods: 
                    if(self.session.query(Association).filter(Association.link_id == row.id).count() == 1): # if only one user uses link
                        self.session.query(Association)\
                            .filter(Association.link_id == row.id)\
                            .delete()
                        self.session.delete(row) # delete link
                    else:  # delete only association
                        self.session.query(Association)\
                            .filter(Association.user_id == userId)\
                            .delete()
                self.session.commit()
            except Exception as e:
                print(e)
            
            #s = self.users.delete().where(self.users.c.tlg_id == tlg_id)

    def get_tlg_id(self, link_id):
        user = self.session.query(User.tlg_id).join(Association, Link).\
                            filter(Link.id == link_id).all()
        return user

    def hour_pars(self, notify):
        logger = logging.getLogger("botLogger.mydatabase.hour_pars")
        logger.info("hour parsing started")

        threading.Timer(3600.0, self.hour_pars, [notify]).start()
        link_to_pars = True
        now = datetime.utcnow()
        hour_ago = now - timedelta(minutes=60)
        try:
            while link_to_pars:                
                link_to_pars = self.session.query(Link).filter(
                    Link.updated_at < hour_ago).filter(Link.archive == 0).first()
                
                if link_to_pars:
                    logger.info("link to pars "+ str(link_to_pars))
                    new_price, state, archive = get_price(link_to_pars.link)
                    notification = {
                        "link" : link_to_pars.link,
                        "price" : link_to_pars.price,
                        "new_price" : new_price,
                        "archive": archive,
                        "old": False
                    }
                    if archive:                    
                        #link_to_pars.archive = 1
                        tlg_id_list = self.get_tlg_id(link_to_pars.id)
                        for tlg_id in tlg_id_list:
                            notification["tlg_id"] = tlg_id.tlg_id
                            self.delete_link(notification["tlg_id"], link_to_pars.id)
                            notify(notification)
                        break
                    else:
                        if link_to_pars.price != new_price:
                            tlg_id_list = self.get_tlg_id(link_to_pars.id)
                            for tlg_id in tlg_id_list:
                                notification["tlg_id"] = tlg_id.tlg_id
                                notify(notification)
                            link_to_pars.price = new_price
                        link_to_pars.state = state
                        
                    now = datetime.utcnow()
                    link_to_pars.updated_at = now
            self.session.commit()
            logger.info("hour parsing successfully ended")
        except Exception as ex:
            print(ex)
            logger.exception("Error while parsing!" + str(ex) +
                             "link_to_pars: " + str(link_to_pars))
   
    def del_old(self, notify):
        # works once in 1 day

        logger = logging.getLogger("botLogger.mydatabase.del_old")
        logger.info("old links deleting started")

        threading.Timer(86400.0, self.del_old, [notify]).start()
        now = datetime.utcnow()
        two_week_ago = now - timedelta(days=3)                      
        try:
            to_del = self.session.query(Association).join(User, Link).filter(
                        Association.created_at < two_week_ago).all()
            if to_del:
                logger.info("links to delete: ", to_del)
                for row in to_del:                                       
                    notification = {
                        "link": row.link.link,
                        "tlg_id": row.user.tlg_id,
                        "price": None,
                        "new_price": None,
                        "archive": None,
                        "old" : True
                    }
                    notify(notification)
                    count = self.session.query(Association).filter(
                        Association.link_id == row.link.id).count()
                    if(count == 1):
                        self.session.query(Link).filter(Link.id == row.link_id).delete()
                    self.session.query(Association).filter(
                        Association.user_id == row.user_id, Association.link_id == row.link_id).delete()  # Association.id == row.id
            self.session.commit()
            logger.info("old links deleting successfully ended")
        except Exception as ex:
            print(ex)
            logger.exception("Error while deleting old links!" + str(ex)
                             )
