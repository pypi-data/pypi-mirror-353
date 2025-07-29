import random
import string
from typing import Literal, Union
import uuid

from faker import Faker

fake = Faker()

date_formats = Literal[
    "YYYY-MM-dd",
    "dd-MM-YYYY",
    "YYYY/MM/dd",
    "dd/MM/YYYY"
]


def generate_random_int(minimum: int = 0, maximum: int = 10000):
    return random.randint(minimum, maximum)


def generate_random_float(minimum: float = 0.0, maximum: float = 10000.0, decimal_places: int = 0):
    return round(random.uniform(minimum, maximum), decimal_places)


def generate_random_string(length: int = 4, case: Union["upper, lower, mix"] = "lower"):
    if case == "upper":
        return ''.join(random.choice(string.ascii_uppercase) for i in range(length))
    elif case == "mix":
        return ''.join(random.choice(string.ascii_letters) for i in range(length))
    else:
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def generate_random_name():
    return fake.name()


def generate_random_uuid():
    return uuid.uuid4()


def generate_random_boolean():
    return bool(random.getrandbits(1))


def generate_date_string(date_fomat: date_formats = "YYYY-MM-dd"):
    fake_date = fake.date()
    fake_year = fake_date[:4]
    fake_month = fake_date[5:7]
    fake_day = fake_date[8:10]

    if date_fomat == "YYYY-MM-dd":
        return f"{fake_year}-{fake_month}-{fake_day}"
    elif date_fomat == "dd-MM-YYYY":
        return f"{fake_day}-{fake_month}-{fake_year}"
    elif date_fomat == "YYYY/MM/dd":
        return f"{fake_year}/{fake_month}/{fake_day}"
    elif date_fomat == "dd/MM/YYYY":
        return f"{fake_day}/{fake_month}/{fake_year}"


