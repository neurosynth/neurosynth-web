from math import pi, sqrt, radians, sin, cos
from nsweb.models.studies import Peak

'''
This file is currently the placeholder for me to play with euclidean distance calculations and optimize it for DB. precalculating isn't faster.
I'm wondering if boxing prior and running a second select would be faster since we'd get results into memory that way!
'''

Peak = classmethod(lambda s: (s.x, s.y, s.z))

def calc_distance(xyz1, xyz2):
    return func.sqrt(func.pow((xyz1[0] - xyz2[0]),2)
                   + func.pow((xyz1[1] - xyz2[2]),2)
                   + func.pow((xyz1[2] - xyz2[2]),2))

def distance():
    pass

def closeSphere(radius, (x,y,z)):
    pass
    
def closeCube(edge_length, (x,y,z)):
    return x< x+edge_length && x>x-edge_length && y< y+edge_length && y>y-edge_length && z< z+edge_length && z>z-edge_length