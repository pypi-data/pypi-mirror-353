import abc

from unitelabs.cdk import sila


class GreetingProviderBase(sila.Feature, metaclass=abc.ABCMeta):
    """
    Example implementation of a minimum Feature.

    Provide a Greeting to the Client and a StartYear property, informing about the year the Server has been started.
    """

    def __init__(self):
        super().__init__(
            originator="org.silastandard",
            category="examples",
            version="1.0",
            maturity_level="Verified",
        )

    @abc.abstractmethod
    @sila.UnobservableCommand()
    @sila.Response(name="Greeting")
    async def say_hello(self, name: str) -> str:
        """
        Say "Hello SiLA 2" + `name`..

        .. parameter:: The name, SayHello shall use to greet.
        .. return: The greeting string, returned to the SiLA Client.
        """

    @abc.abstractmethod
    @sila.UnobservableProperty()
    async def start_year(self) -> int:
        """Get the year the SiLA Server has been started in."""
