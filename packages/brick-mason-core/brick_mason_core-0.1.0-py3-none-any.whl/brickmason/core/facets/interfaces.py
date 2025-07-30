import abc
from ..configuration.interfaces import IConfigurationContainer


class IJinjaFacet(metaclass=abc.ABCMeta):
    """Represents a Jinja facet."""

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:  # noqa: D105, FNE005
        return (
            hasattr(subclass, "parameters")
            and hasattr(subclass, "macros")
            and hasattr(subclass, "render")
            and callable(subclass.render)
            and hasattr(subclass, "render_file")
            and callable(subclass.render_file)
            or NotImplemented
        )

    @property
    @abc.abstractmethod
    def parameters(self) -> IConfigurationContainer:
        """Get the Jinja environment."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def macros(self) -> IConfigurationContainer:
        """Get the Jinja macros."""
        raise NotImplementedError

    @abc.abstractmethod
    def render(self, template: str, **kwargs) -> str:
        """Render the Jinja template with the given context."""
        raise NotImplementedError

    @abc.abstractmethod
    def render_file(self, file_path: str, **kwargs) -> str:
        """Render the Jinja template fram a file."""
        raise NotImplementedError
