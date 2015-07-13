# from unittest import TestCase
# from runserver import main
# import thread, time
# from nsweb.core import app

# class Test(TestCase):
        
#     def test_runserver_works(self):
#         def tryit():
#             with app.test_request_context():
#                 from flask import request

#             time.sleep(3)
#             func = request.environ.get('werkzeug.server.shutdown')
#             if func is not None:
#                 assert True
#                 func()
#             else: assert False
        
#             thread.start_new_thread(tryit())
#             thread.start_new_thread(main())
            
