import os
from collections import namedtuple
import pytest
from tests.common import rp

def repr_param(param):
    return "{:15s}".format(param)


@pytest.fixture(params=[
    rp("../data/huge_iris.dat"),
    rp("../data/iris.dat"),
],
    ids=repr_param)
def data_file(request):
    param = request.param
    return param
