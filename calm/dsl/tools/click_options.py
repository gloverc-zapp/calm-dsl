import click

from calm.dsl.config import get_config
from .logger import CustomLogging, set_verbose_level


def simple_verbosity_option(logging_mod=None, *names, **kwargs):
    """A decorator that adds a `--verbose, -v` option to the decorated
    command.
    Name can be configured through ``*names``. Keyword arguments are passed to
    the underlying ``click.option`` decorator.
    """

    if not names:
        names = ["--verbose", "-v"]

    if not isinstance(logging_mod, CustomLogging):
        raise TypeError("Logging object should be instance of CustomLogging.")

    log_level = "INFO"
    try:
        # At the time of initializing dsl, config file may not be present
        config = get_config()
        if "LOG" in config:
            log_level = config["LOG"].get("level") or log_level

    except FileNotFoundError:
        pass

    logging_levels = logging_mod.get_logging_levels()
    if log_level not in logging_levels:
        raise ValueError(
            "Invalid log level in config. Select from {}".format(logging_levels)
        )

    log_level = logging_levels.index(log_level) + 1
    kwargs.setdefault("default", log_level)
    kwargs.setdefault("expose_value", False)
    kwargs.setdefault("help", "Verboses the output")
    kwargs.setdefault("is_eager", True)
    kwargs.setdefault("count", True)

    def decorator(f):
        def _set_level(ctx, param, value):
            logging_levels = logging_mod.get_logging_levels()
            if value < 1 or value > len(logging_levels):
                raise click.BadParameter(
                    "Should be atleast 1 and atmost {}".format(len(logging_levels))
                )

            log_level = logging_levels[value - 1]
            x = getattr(logging_mod, log_level, None)
            logging_mod.set_logger_level(x)
            set_verbose_level(x)

        return click.option(*names, callback=_set_level, **kwargs)(f)

    return decorator