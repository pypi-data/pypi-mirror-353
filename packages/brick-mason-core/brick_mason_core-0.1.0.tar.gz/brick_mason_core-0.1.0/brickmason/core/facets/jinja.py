from jinja2 import Environment
from ..configuration.interfaces import IConfigurationContainer
from .interfaces import IJinjaFacet


class JinjaFacet(IJinjaFacet):
    """Implementation of the Jinja facet."""

    def __init__(
        self,
        jinja_parameters: IConfigurationContainer,
        jinja_macros: IConfigurationContainer,
    ) -> None:
        super().__init__()
        self.__parameters: IConfigurationContainer = jinja_parameters
        self.__macros: IConfigurationContainer = jinja_macros

    @property
    def parameters(self) -> IConfigurationContainer:
        """Get the Jinja parameters."""
        return self.__parameters

    @property
    def macros(self) -> IConfigurationContainer:
        """Get the Jinja macros."""
        return self.__macros

    def render(self, template: str, **kwargs) -> str:
        """Render the Jinja template with the given context."""
        env = self.__create_environment()
        render_template = env.from_string(template)
        params = {
            **self.parameters.build(),
            **kwargs,
        }
        return render_template.render(**params)

    def render_file(self, file_path: str, **kwargs) -> str:
        """Render the Jinja template from a file."""
        with open(file_path, "r", encoding="utf-8") as f:
            template = f.read()

        return self.render(template, **kwargs)

    def __create_environment(self) -> Environment:
        """Create the Jinja environment."""
        env = Environment()
        macro_module = env.from_string(self.__combine_macro_values()).module
        for name in dir(macro_module):
            if name.startswith("_"):
                continue

            attr = getattr(macro_module, name)
            if callable(attr):
                env.globals[name] = attr

        return env

    def __combine_macro_values(self) -> str:
        """Combine the macro to the source."""
        # Implementation would go here
        return "\n\n".join(macro for macro in list(self.macros.build().values()))
