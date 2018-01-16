import os
from collections import namedtuple
import pytest


# from tests.common import *


def rp(path):
    return os.path.join(os.path.dirname(__file__), path)


NormSettings = namedtuple('NormSettings', 'enabled center spread')


def repr_param(param):
    return "{:15s}".format(param)


@pytest.fixture(params=[
    rp("../../data/iris.dat"),
])
def iris(request):
    param = request.param
    return param


@pytest.fixture(params=[
    NormSettings(True, "Mean", "Semi range"),
], )
def norm_settings(request):
    param = request.param
    return param


@pytest.fixture(params=[
    "raw", "norm"
], )
def table_type(request):
    return request.param
