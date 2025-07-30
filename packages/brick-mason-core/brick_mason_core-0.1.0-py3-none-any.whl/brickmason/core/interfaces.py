import abc
from .configuration.interfaces import IConfigurationManager
from .facets.interfaces import IJinjaFacet


class ITarget(abc.ABC):
    """Represents a target."""

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:  # noqa: D105, FNE005
        return (
            hasattr(subclass, "conf") and hasattr(subclass, "jinja") or NotImplemented
        )

    @property
    @abc.abstractmethod
    def conf(self) -> IConfigurationManager:
        """Get the configuration manager."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def jinja(self) -> IJinjaFacet:
        """Get the Jinja facet."""
        raise NotImplementedError
