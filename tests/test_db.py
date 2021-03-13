from datetime import datetime
import pytest

import arrow
from mongoengine import connect, disconnect, Document

from sizebot.lib.db import ArrowField


@pytest.fixture
def db():
    db = connect('dbtest', host='mongomock://localhost')
    yield db
    disconnect()


class ArrowTest(Document):
    mydate = ArrowField()

    def __str__(self):
        return repr(self.mydate)


def test_arrow_none(db):
    t = ArrowTest(mydate=None)
    t.save()
    t_saved = ArrowTest.objects(id=t.id).first()
    assert t_saved.mydate is None


def test_arrow_int(db):
    t = ArrowTest(mydate=0)
    t.save()
    t_saved = ArrowTest.objects(id=t.id).first()
    assert isinstance(t_saved.mydate, arrow.Arrow)
    assert t_saved.mydate == arrow.get("1970-01-01T00:00:00+00:00")


def test_arrow_datetime(db):
    t = ArrowTest(mydate=datetime.fromtimestamp(0))
    t.save()
    t_saved = ArrowTest.objects(id=t.id).first()
    assert isinstance(t_saved.mydate, arrow.Arrow)
    assert t_saved.mydate == arrow.get("1969-12-31T19:00:00+00:00")


def test_arrow_arrow(db):
    t = ArrowTest(mydate=arrow.Arrow.utcfromtimestamp(0))
    t.save()
    t_saved = ArrowTest.objects(id=t.id).first()
    assert isinstance(t_saved.mydate, arrow.Arrow)
    assert t_saved.mydate == arrow.get("1970-01-01T00:00:00+00:00")


def test_compare(db):
    a_small = arrow.Arrow.utcfromtimestamp(0)
    a_big = arrow.Arrow.utcfromtimestamp(1000)
    t_small = ArrowTest(mydate=a_small)
    t_small.save()
    assert ArrowTest.objects(mydate__lte=a_big).count() == 1
