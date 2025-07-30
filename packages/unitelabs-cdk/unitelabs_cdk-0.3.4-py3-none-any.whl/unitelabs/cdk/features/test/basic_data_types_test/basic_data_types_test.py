from unitelabs.cdk import sila


class BasicDataTypesTest(sila.Feature):
    """Set or get all SiLA Basic Data Types via command parameters or property responses respectively."""

    def __init__(self):
        super().__init__(
            originator="org.silastandard",
            category="test",
            version="1.0",
        )

    # Data type String

    @sila.UnobservableProperty()
    def get_string_value(self) -> str:
        """Return the String value 'SiLA2_Test_String_Value'."""
        return "SiLA2_Test_String_Value"

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_string_value(self, string_value: str) -> str:
        """
        Receives a String value and returns the String value that has been received.

        .. parameter:: The String value to be returned.
        .. return:: The String value that has been received.
        """
        return string_value

    # Data type Integer

    @sila.UnobservableProperty()
    def get_integer_value(self) -> int:
        """Return the Integer value 5124."""
        return 5124

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_integer_value(self, integer_value: int) -> int:
        """
        Receive an Integer value and return the Integer value that has been received.

        .. parameter:: The Integer value to be returned.
        .. return:: The Integer value that has been received.
        """
        return integer_value

    # Data type Real

    @sila.UnobservableProperty()
    def get_real_value(self) -> float:
        """Return the Real value 3.1415926."""
        return 3.1415926

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_real_value(self, real_value: float) -> float:
        """
        Receive a Real value and return the Real value that has been received.

        .. parameter:: The Real value to be returned.
        .. return:: The Real value that has been received.
        """
        return real_value

    # Data type Boolean

    @sila.UnobservableProperty()
    def get_boolean_value(self) -> bool:
        """Return the Boolean value true."""
        return True

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_boolean_value(self, boolean_value: bool) -> bool:
        """
        Receive a Boolean value and return the Boolean value that has been received.

        .. parameter:: The Boolean value to be returned.
        .. return:: The Boolean value that has been received.
        """
        return boolean_value

    # Data type Date

    @sila.UnobservableProperty()
    def get_date_value(self) -> sila.datetime.date:
        """Return the Date value 05.08.2022 respective 08/05/2018, timezone +2."""
        return sila.datetime.date(
            year=2022, month=8, day=5, tzinfo=sila.datetime.timezone(offset=sila.datetime.timedelta(hours=+2))
        )

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_date_value(self, date_value: sila.datetime.date) -> sila.datetime.date:
        """
        Receive a Date value and return the Date value that has been received.

        .. parameter:: The Date value to be returned.
        .. return:: The Date value that has been received.
        """
        return date_value

    # Data type Time

    @sila.UnobservableProperty()
    def get_time_value(self) -> sila.datetime.time:
        """Return the Time value 12:34:56.789, timezone +2."""
        return sila.datetime.time(
            hour=12,
            minute=34,
            second=56,
            microsecond=789000,
            tzinfo=sila.datetime.timezone(offset=sila.datetime.timedelta(hours=+2)),
        )

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_time_value(self, time_value: sila.datetime.time) -> sila.datetime.time:
        """
        Receive a Time value and return the Time value that has been received.

        .. parameter:: The Time value to be returned.
        .. return:: The Time value that has been received.
        """
        return time_value

    # Data type Timestamp

    @sila.UnobservableProperty()
    def get_timestamp_value(self) -> sila.datetime.datetime:
        """Return the Timestamp value 2022-08-05 12:34:56.789, timezone +2."""
        return sila.datetime.datetime(
            year=2022,
            month=8,
            day=5,
            hour=12,
            minute=34,
            second=56,
            microsecond=789000,
            tzinfo=sila.datetime.timezone(offset=sila.datetime.timedelta(hours=+2)),
        )

    @sila.UnobservableCommand()
    @sila.Response(name="Received Value")
    def echo_timestamp_value(self, timestamp_value: sila.datetime.datetime) -> sila.datetime.datetime:
        """
        Receive a Timestamp value and return the Timestamp value that has been received.

        .. parameter:: The Timestamp value to be returned.
        .. return:: The Timestamp value that has been received.
        """
        return timestamp_value
