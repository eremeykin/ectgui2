import os
from collections import namedtuple
import pytest
# from tests.common import *


def rp(path):
    return os.path.join(os.path.dirname(__file__), path)


NormSettings = namedtuple('NormSettings', 'enabled center spread power')


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


@pytest.fixture(params=[
    rp("../data/iris.dat"),
])
def small_file(request):
    param = request.param
    return param


@pytest.fixture(params=[
    NormSettings(True, "Mean", "Semi range", None),
], )
def norm_settings(request):
    param = request.param
    return param


@pytest.fixture(params=[
    "raw", "norm"
], )
def table_type(request):
    return request.param
