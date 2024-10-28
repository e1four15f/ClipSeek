from typing import Any


class DocstringMixin:
    def __init_subclass__(cls, **kwargs: Any):  # noqa: ANN401
        super().__init_subclass__(**kwargs)
        for name, method in cls.__dict__.items():
            if callable(method) and name in cls.__bases__[0].__dict__:
                # Copy docstring from the abstract method
                method.__doc__ = cls.__bases__[0].__dict__[name].__doc__
