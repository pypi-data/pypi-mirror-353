import pytest

from nemo_library import NemoLibrary
from datetime import datetime

from nemo_library.utils.utils import FilterType, FilterValue
from tests.testutils import getNL

META_PROJECT_NAME = "Business Processes"


def t_est_create():
    nl = getNL()
    nl.MetaDataCreate(
        projectname=META_PROJECT_NAME,
        filter="optimate",
        filter_type=FilterType.STARTSWITH,
        filter_value=FilterValue.INTERNALNAME,
    )


def t_est_load():
    nl = getNL()
    nl.MetaDataLoad(
        projectname=META_PROJECT_NAME,
        filter="optimate",
        filter_type=FilterType.STARTSWITH,
        filter_value=FilterValue.INTERNALNAME,
    )


def t_est_delete():
    nl = getNL()
    nl.MetaDataDelete(
        projectname=META_PROJECT_NAME,
        filter="optimate",
        filter_type=FilterType.STARTSWITH,
        filter_value=FilterValue.INTERNALNAME,
    )
