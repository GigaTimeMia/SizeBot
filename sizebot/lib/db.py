import arrow
from mongoengine.fields import DateTimeField, StringField

from sizebot.lib.units import SV, WV, TV


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


class UnitField(StringField):
    UNIT_CLASS = None

    def to_python(self, value):
        value = super().to_python(value)
        if isinstance(value, str):
            value = self.UNIT_CLASS(value)
        return value

    def to_mongo(self, value):
        return str(value)

    def validate(self, value):
        if not isinstance(value, self.UNIT_CLASS):
            self.error(f"{value} is not a {self.UNIT_CLASS.__name__}")


class SVField(UnitField):
    UNIT_CLASS = SV


class WVField(UnitField):
    UNIT_CLASS = WV


class TVField(UnitField):
    UNIT_CLASS = TV


class SnowflakeField(StringField):
    def to_mongo(self, value):
        print("TO_MONGO")
        if value is not None:
            value = str(value)
        return value

    def to_python(self, value):
        print("TO_PYTHON")
        value = super().to_python(value)
        if value is not None:
            value = int(value)
        return value

    def validate(self, value):
        print("VALIDATE")
        min_value = 0x0000000000000000
        max_value = 0xFFFFFFFFFFFFFFFF
        try:
            value = int(value)
        except (TypeError, ValueError):
            self.error(f"{value} could not be converted to int")

        if value < min_value:
            self.error("Snowflake value is too small")

        if value > max_value:
            self.error("Snowflake value is too large")
