import arrow
from mongoengine.fields import DateTimeField


class ArrowField(DateTimeField):
    def to_mongo(self, value):
        if value is not None:
            value = value.datetime
        return super().to_mongo(value)

    def to_python(self, value):
        value = super().to_python(value)
        if value is not None:
            value = arrow.get(value)
        return value
