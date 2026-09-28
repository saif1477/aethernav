import numpy as np

from aethernav.coordinates.enu import enu_to_wgs84, wgs84_to_enu


def test_origin_is_zero():
    x=wgs84_to_enu([13.0],[80.0],[10.0]); assert np.allclose(x,0,atol=1e-9)

def test_round_trip():
    origin=(13.0,80.0,10.0); geo=np.array([[13.0,80.0,10.0],[13.001,80.002,12.0]])
    enu=wgs84_to_enu(geo[:,0],geo[:,1],geo[:,2],origin); restored=enu_to_wgs84(enu,origin)
    assert np.allclose(restored,geo,atol=1e-7)
