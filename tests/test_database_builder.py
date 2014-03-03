from tests import *

class Test(TestCase):

    def test_initialize_database(self):
        '''Clears and sets up tables in database. The tables in studies, features, and images should exist, but no data'''
        database_builder.init_database(self.db)
        asdf = self.db.Query.all()
        
if __name__ == "__main__":
    import nose
    nose.run()