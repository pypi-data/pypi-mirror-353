"""
Test module for the StringDateMother class.
"""

from datetime import UTC, datetime

from dateutil.relativedelta import relativedelta
from pytest import mark, raises as assert_raises

from object_mother_pattern.mothers import DateMother, IntegerMother, StringDateMother


@mark.unit_testing
def test_string_date_mother_happy_path() -> None:
    """
    Test StringDateMother happy path.
    """
    value = StringDateMother.create()

    assert type(value) is str


@mark.unit_testing
def test_string_date_mother_value() -> None:
    """
    Test StringDateMother create method with value.
    """
    value = StringDateMother.create()

    assert StringDateMother.create(value=value) == value


@mark.unit_testing
def test_string_date_mother_invalid_type() -> None:
    """
    Test StringDateMother create method with invalid type.
    """
    assert type(StringDateMother.invalid_type()) is not str


@mark.unit_testing
def test_string_date_mother_invalid_value() -> None:
    """
    Test StringDateMother invalid_value method.
    """
    value = StringDateMother.invalid_value()

    assert type(value) is str
    assert not value.isprintable()


@mark.unit_testing
def test_string_date_mother_invalid_value_type() -> None:
    """
    Test StringDateMother create method with invalid value type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match='StringDateMother value must be a str.',
    ):
        StringDateMother.create(value=StringDateMother.invalid_type())


@mark.unit_testing
def test_string_date_mother_invalid_start_date_type() -> None:
    """
    Test StringDateMother create method with invalid start_date type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match='DateMother start_date must be a date.',
    ):
        StringDateMother.create(start_date=DateMother.invalid_type())


@mark.unit_testing
def test_string_date_mother_invalid_end_date_type() -> None:
    """
    Test StringDateMother create method with invalid end_date type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match='DateMother end_date must be a date.',
    ):
        StringDateMother.create(end_date=DateMother.invalid_type())


@mark.unit_testing
def test_string_date_mother_start_date_greater_than_end_date() -> None:
    """
    Test StringDateMother create method with start_date greater than end_date.
    """
    start_date = DateMother.create(
        start_date=datetime.now(tz=UTC).date(),
        end_date=datetime.now(tz=UTC).date() + relativedelta(years=100),
    )
    end_date = DateMother.create(
        start_date=datetime.now(tz=UTC).date() - relativedelta(years=100),
        end_date=datetime.now(tz=UTC).date(),
    )

    with assert_raises(
        expected_exception=ValueError,
        match='DateMother end_date must be older than start_date.',
    ):
        StringDateMother.create(start_date=start_date, end_date=end_date)


@mark.unit_testing
def test_string_date_mother_out_of_range_method_happy_path() -> None:
    """
    Test StringDateMother happy path.
    """
    start_date = datetime.now(tz=UTC).date() - relativedelta(years=100)
    end_date = datetime.now(tz=UTC).date()

    value = StringDateMother.out_of_range(start_date=start_date, end_date=end_date)

    assert type(value) is str
    assert (
        start_date >= datetime.fromisoformat(value).date() <= end_date
        or start_date <= datetime.fromisoformat(value).date() >= end_date
    )


@mark.unit_testing
def test_string_date_mother_out_of_range_method_invalid_start_date_type() -> None:
    """
    Test StringDateMother create method with invalid start_date type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match='DateMother start_date must be a date.',
    ):
        StringDateMother.out_of_range(start_date=DateMother.invalid_type())


@mark.unit_testing
def test_string_date_mother_out_of_range_method_invalid_end_date_type() -> None:
    """
    Test StringDateMother create method with invalid end_date type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match='DateMother end_date must be a date.',
    ):
        StringDateMother.out_of_range(end_date=DateMother.invalid_type())


@mark.unit_testing
def test_string_date_mother_out_of_range_method_invalid_range_type() -> None:
    """
    Test StringDateMother create method with invalid range type.
    """
    with assert_raises(
        expected_exception=TypeError,
        match='DateMother range must be an integer.',
    ):
        StringDateMother.out_of_range(range=IntegerMother.invalid_type())


@mark.unit_testing
def test_string_date_mother_out_of_range_method_invalid_range_value() -> None:
    """
    Test StringDateMother create method with invalid range value.
    """
    with assert_raises(
        expected_exception=ValueError,
        match='DateMother range must be a positive integer.',
    ):
        StringDateMother.out_of_range(range=IntegerMother.negative())


@mark.unit_testing
def test_string_date_mother_out_of_range_method_start_date_greater_than_end_date() -> None:
    """
    Test StringDateMother create method with start_date greater than end_date.
    """
    start_date = DateMother.create(
        start_date=datetime.now(tz=UTC).date(),
        end_date=datetime.now(tz=UTC).date() + relativedelta(years=100),
    )
    end_date = DateMother.create(
        start_date=datetime.now(tz=UTC).date() - relativedelta(years=100),
        end_date=datetime.now(tz=UTC).date(),
    )

    with assert_raises(
        expected_exception=ValueError,
        match='DateMother end_date must be older than start_date.',
    ):
        StringDateMother.out_of_range(start_date=start_date, end_date=end_date)
