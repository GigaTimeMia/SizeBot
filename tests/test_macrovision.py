import asyncio
from sizebot.lib import macrovision, units
from sizebot.lib.decimal import Decimal
from sizebot.lib.units import SV

asyncio.run(units.init())


def test_macrovision():
    assert macrovision.get_url([
        {"name": "Duncan", "model": "man1", "height": Decimal("0.0127")},
        {"name": "Natalie", "model": "woman1", "height": Decimal("0.1524")}
    ]) == "https://macrovision.crux.sexy/?scene=eyJlbnRpdGllcyI6IFt7Im5hbWUiOiAiSHVtYW4iLCAiY3VzdG9tTmFtZSI6ICJOYXRhbGllIiwgInNjYWxlIjogMC4wODk1NTIyMzg4MDU5NzAxNCwgInZpZXciOiAid29tYW4xIiwgIngiOiAiMCIsICJ5IjogIjAiLCAicHJpb3JpdHkiOiAwLCAiYnJpZ2h0bmVzcyI6IDF9LCB7Im5hbWUiOiAiSHVtYW4iLCAiY3VzdG9tTmFtZSI6ICJEdW5jYW4iLCAic2NhbGUiOiAwLjAwNzA0MjI1MzUyMTEyNjc2MSwgInZpZXciOiAibWFuMSIsICJ4IjogIjAuMDM4MSIsICJ5IjogIjAiLCAicHJpb3JpdHkiOiAwLCAiYnJpZ2h0bmVzcyI6IDF9XSwgIndvcmxkIjogeyJoZWlnaHQiOiAwLjE1MjQsICJ1bml0IjogIm1ldGVycyIsICJ4IjogIjAiLCAieSI6ICIwIn0sICJ2ZXJzaW9uIjogM30="


def test_macrovision_SV():
    assert macrovision.get_url([
        {"name": "Duncan", "model": "man1", "height": SV.parse("0.5in")},
        {"name": "Natalie", "model": "woman1", "height": SV.parse("6in")}
    ]) == "https://macrovision.crux.sexy/?scene=eyJlbnRpdGllcyI6IFt7Im5hbWUiOiAiSHVtYW4iLCAiY3VzdG9tTmFtZSI6ICJOYXRhbGllIiwgInNjYWxlIjogMC4wODk1NTIyMzg4MDU5NzAxNCwgInZpZXciOiAid29tYW4xIiwgIngiOiAiMCIsICJ5IjogIjAiLCAicHJpb3JpdHkiOiAwLCAiYnJpZ2h0bmVzcyI6IDF9LCB7Im5hbWUiOiAiSHVtYW4iLCAiY3VzdG9tTmFtZSI6ICJEdW5jYW4iLCAic2NhbGUiOiAwLjAwNzA0MjI1MzUyMTEyNjc2MSwgInZpZXciOiAibWFuMSIsICJ4IjogIjAuMDM4MSIsICJ5IjogIjAiLCAicHJpb3JpdHkiOiAwLCAiYnJpZ2h0bmVzcyI6IDF9XSwgIndvcmxkIjogeyJoZWlnaHQiOiAwLjE1MjQsICJ1bml0IjogIm1ldGVycyIsICJ4IjogIjAiLCAieSI6ICIwIn0sICJ2ZXJzaW9uIjogM30="


def test_weird_names():
    assert macrovision.get_url([
        {"name": r"r'(?<!\.)[.?!](?!\.)', z [1.22m]", "model": "man1", "height": Decimal("1.219")},
        {"name": "Natalie", "model": "woman1", "height": Decimal("0.1524")}
    ]) == "https://macrovision.crux.sexy/?scene=eyJlbnRpdGllcyI6IFt7Im5hbWUiOiAiSHVtYW4iLCAiY3VzdG9tTmFtZSI6ICJyJyg/PCFcXC4pWy4/IV0oPyFcXC4pJywgeiBbMS4yMm1dIiwgInNjYWxlIjogMC42NzU5NDU0MzYzOTc5MTUsICJ2aWV3IjogIm1hbjEiLCAieCI6ICIwIiwgInkiOiAiMCIsICJwcmlvcml0eSI6IDAsICJicmlnaHRuZXNzIjogMX0sIHsibmFtZSI6ICJIdW1hbiIsICJjdXN0b21OYW1lIjogIk5hdGFsaWUiLCAic2NhbGUiOiAwLjA4OTU1MjIzODgwNTk3MDE0LCAidmlldyI6ICJ3b21hbjEiLCAieCI6ICIwLjMwNDc1IiwgInkiOiAiMCIsICJwcmlvcml0eSI6IDAsICJicmlnaHRuZXNzIjogMX1dLCAid29ybGQiOiB7ImhlaWdodCI6IDEuMjE5LCAidW5pdCI6ICJtZXRlcnMiLCAieCI6ICIwIiwgInkiOiAiMCJ9LCAidmVyc2lvbiI6IDN9"
