'''
Created on Mar 23, 2012

@package: ally core sql alchemy
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the sql alchemy mapper.
'''

import unittest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Table, Column, MetaData, ForeignKey
from sqlalchemy.dialects.mysql.base import INTEGER
from sqlalchemy.types import String
from ally.api.config import model
from ally.support.sqlalchemy.mapper import mapperSimple
from ally.api.type import typeFor

# --------------------------------------------------------------------

meta = MetaData()

tableUser = Table('user', meta,
                  Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
                  Column('name', String(20), nullable=False, unique=True, key='Name'))

tableParent = Table('user_parent', meta,
                    Column('id', INTEGER(unsigned=True), primary_key=True, key='Id'),
                    Column('name', String(20), nullable=False, unique=True, key='Name'))

tableUserParent = Table('user_with_parent', meta,
                Column('fk_user_id', INTEGER(unsigned=True), ForeignKey(tableUser.c.Id), primary_key=True, key='Id'),
                Column('fk_parent_id', INTEGER(unsigned=True), ForeignKey(tableParent.c.Id), key='Parent'))

@model(id='Id')
class User:
    '''    
    Provides the user model.
    '''
    Id = int
    Name = str

@model(id='Id')
class Parent:
    '''    
    Provides the user parent.
    '''
    Id = int
    Name = str

@model
class UserWithParent(User):
    '''
    A user model with a parent.
    '''
    Parent = Parent

# --------------------------------------------------------------------

class TestMapping(unittest.TestCase):

    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        self.sessionCreate = sessionmaker(bind=engine)
        meta.create_all(engine)

    def testSuccesSimpleMapping(self):
        User = mapperSimple(globals()['User'], tableUser)

        self.assertTrue(typeFor(User.Id).isOf(int))
        self.assertTrue(typeFor(User.Name).isOf(str))

        session = self.sessionCreate()
        user = User()
        self.assertTrue(User.Id not in user)
        self.assertTrue(User.Name not in user)

        user.Name = 'Hello world'
        self.assertTrue(User.Name in user)
        self.assertTrue(User.Id not in user)

        session.add(user)
        session.flush((user,))
        self.assertTrue(User.Id in user)

        session.commit()
        session.close()

        session = self.sessionCreate()
        users = session.query(User).filter(User.Name == 'Hello world').all()
        self.assertEqual(len(users), 1)
        self.assertTrue(User.Id in users[0])
        self.assertTrue(User.Name in users[0])
        self.assertEqual(users[0].Name, 'Hello world')
        self.assertEqual(users[0].Id, 1)
        session.close()

    def testSuccessInheritAndForeignKey(self):
        User = mapperSimple(globals()['User'], tableUser)

        UserWithParent = mapperSimple(globals()['UserWithParent'], tableUserParent, inherits=User)

        self.assertTrue(typeFor(UserWithParent.Id).isOf(int))
        self.assertTrue(typeFor(UserWithParent.Name).isOf(str))
        self.assertTrue(typeFor(UserWithParent.Parent).isOf(Parent))
        self.assertTrue(typeFor(UserWithParent.Parent.Id).isOf(int))
        self.assertTrue(typeFor(UserWithParent.Parent.Name).isOf(str))

        session = self.sessionCreate()
        user = UserWithParent()
        self.assertTrue(UserWithParent.Id not in user)
        self.assertTrue(UserWithParent.Name not in user)
        self.assertTrue(UserWithParent.Parent not in user)

        user.Name = 'Hello world'
        self.assertTrue(UserWithParent.Name in user)

        user.Parent = 1
        self.assertTrue(UserWithParent.Parent in user)
        self.assertTrue(UserWithParent.Id not in user)

        session.add(user)
        session.flush((user,))
        self.assertTrue(UserWithParent.Id in user)

        session.commit()
        session.close()

        session = self.sessionCreate()
        users = session.query(UserWithParent).filter(UserWithParent.Name == 'Hello world').all()
        self.assertEqual(len(users), 1)
        self.assertTrue(UserWithParent.Id in users[0])
        self.assertTrue(UserWithParent.Name in users[0])
        self.assertTrue(UserWithParent.Parent in users[0])
        self.assertEqual(users[0].Name, 'Hello world')
        self.assertEqual(users[0].Id, 1)
        self.assertEqual(users[0].Parent, 1)
        session.close()

    # ----------------------------------------------------------------

    def testFailedExtending(self):
        User = mapperSimple(globals()['User'], tableUser)

        def extendMapped():
            class UserExt(User):
                pass
        self.assertRaises(TypeError, extendMapped)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
