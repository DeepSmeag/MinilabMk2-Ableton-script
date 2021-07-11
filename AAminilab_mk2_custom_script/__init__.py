from __future__ import absolute_import, print_function, unicode_literals
from .test import test   # you import your main program during the initialisation of your script


def create_instance(c_instance):    # this function tells live that you create a new midi remote script
    return test(c_instance)  
