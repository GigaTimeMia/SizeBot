from datetime import datetime
from sizebot.lib.units import SV, WV, TV

import arrow
import pytest
from mongoengine import Document, connect, disconnect
from mongoengine.errors import ValidationError

from sizebot.lib.db import ArrowField, SnowflakeField, SVField, WVField, TVField


@pytest.fixture
def db():
    db = connect('dbtest', host='mongomock://localhost')
    yield db
    disconnect()


class ArrowDoc(Document):
    mydate = ArrowField()


def test_arrow_none(db):
    t = ArrowDoc(mydate=None)
    t.save()
    t_saved = ArrowDoc.objects(id=t.id).first()
    assert t_saved.mydate is None


def test_arrow_int(db):
    t = ArrowDoc(mydate=0)
    t.save()
    t_saved = ArrowDoc.objects(id=t.id).first()
    assert isinstance(t_saved.mydate, arrow.Arrow)
    assert t_saved.mydate == arrow.get("1970-01-01T00:00:00+00:00")


def test_arrow_datetime(db):
    t = ArrowDoc(mydate=datetime.utcfromtimestamp(0))
    t.save()
    t_saved = ArrowDoc.objects(id=t.id).first()
    assert isinstance(t_saved.mydate, arrow.Arrow)
    assert t_saved.mydate == arrow.get("1970-01-01T00:00:00+00:00")


def test_arrow_arrow(db):
    t = ArrowDoc(mydate=arrow.Arrow.utcfromtimestamp(0))
    t.save()
    t_saved = ArrowDoc.objects(id=t.id).first()
    assert isinstance(t_saved.mydate, arrow.Arrow)
    assert t_saved.mydate == arrow.get("1970-01-01T00:00:00+00:00")


def test_compare(db):
    a_small = arrow.Arrow.utcfromtimestamp(0)
    a_big = arrow.Arrow.utcfromtimestamp(1000)
    t_small = ArrowDoc(mydate=a_small)
    t_small.save()
    assert ArrowDoc.objects(mydate__lte=a_big).count() == 1


class SnowflakeDoc(Document):
    snow = SnowflakeField()


def test_snowflake_max(db):
    max_snowflake = 0xFFFFFFFFFFFFFFFF
    doc = SnowflakeDoc(snow=max_snowflake)
    doc.save()
    doc_saved = SnowflakeDoc.objects(id=doc.id).first()
    assert doc_saved.snow == max_snowflake


def test_snowflake_min(db):
    min_snowflake = 0x0000000000000000
    doc = SnowflakeDoc(snow=min_snowflake)
    doc.save()
    doc_saved = SnowflakeDoc.objects(id=doc.id).first()
    assert doc_saved.snow == min_snowflake


def test_snowflake_none(db):
    doc = SnowflakeDoc(snow=None)
    doc.save()
    doc_saved = SnowflakeDoc.objects(id=doc.id).first()
    assert doc_saved.snow is None


def test_snowflake_invalid(db):
    invalid_snowflake = -1
    doc = SnowflakeDoc(snow=invalid_snowflake)
    with pytest.raises(ValidationError):
        doc.save()


class UnitsDoc(Document):
    sv_val = SVField()
    wv_val = WVField()
    tv_val = TVField()


def test_sv(db):
    doc = UnitsDoc(sv_val=SV(1000))
    doc.save()
    doc_saved = UnitsDoc.objects(id=doc.id).first()
    assert isinstance(doc_saved.sv_val, SV)
    assert doc_saved.sv_val == SV(1000)


def test_sv_none(db):
    doc = UnitsDoc(sv_val=None)
    doc.save()
    doc_saved = UnitsDoc.objects(id=doc.id).first()
    assert doc_saved.sv_val is None


def test_sv_invalid(db):
    doc = UnitsDoc(sv_val=WV(1000))
    with pytest.raises(ValidationError):
        doc.save()


def test_wv(db):
    doc = UnitsDoc(wv_val=WV(1000))
    doc.save()
    doc_saved = UnitsDoc.objects(id=doc.id).first()
    assert isinstance(doc_saved.wv_val, WV)
    assert doc_saved.wv_val == WV(1000)


def test_wv_none(db):
    doc = UnitsDoc(wv_val=None)
    doc.save()
    doc_saved = UnitsDoc.objects(id=doc.id).first()
    assert doc_saved.wv_val is None


def test_wv_invalid(db):
    doc = UnitsDoc(wv_val=TV(1000))
    with pytest.raises(ValidationError):
        doc.save()


def test_tv(db):
    doc = UnitsDoc(tv_val=TV(1000))
    doc.save()
    doc_saved = UnitsDoc.objects(id=doc.id).first()
    assert isinstance(doc_saved.tv_val, TV)
    assert doc_saved.tv_val == TV(1000)


def test_tv_none(db):
    doc = UnitsDoc(tv_val=None)
    doc.save()
    doc_saved = UnitsDoc.objects(id=doc.id).first()
    assert doc_saved.tv_val is None


def test_tv_invalid(db):
    doc = UnitsDoc(tv_val=SV(1000))
    with pytest.raises(ValidationError):
        doc.save()
