from math import pi, sqrt, radians, sin, cos
from nsweb.models.studies import Peak
from sqlalchemy import func

'''
This file is currently the placeholder for me to play with euclidean distance calculations and optimize it for DB. precalculating isn't faster.
I'm wondering if boxing prior and running a second select would be faster since we'd get results into memory that way!
'''

# YEa func can't do that....What's sqlalchemy's math functions?!?!

def distance(xyz1, xyz2):
    return func.sqrt(func.pow((xyz1[0] - xyz2[0]),2)
                   + func.pow((xyz1[1] - xyz2[2]),2)
                   + func.pow((xyz1[2] - xyz2[2]),2))


def closeSphere(radius, (x,y,z)):
    pass
    
def closeCube(edge_length, (x,y,z)):
    return x< x+edge_length && x>x-edge_length && y< y+edge_length && y>y-edge_length && z< z+edge_length && z>z-edge_length