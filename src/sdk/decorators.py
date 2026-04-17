from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any


@dataclass(frozen=True)
class ResourceInvocation:
    func: Callable
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    name: str
    table_name: str
    primary_key: str | None = None
    columns: list[str] = field(default_factory=list)
    source_name: str | None = None

    def records(self) -> Iterable:
        return self.func(*self.args, **self.kwargs)


@dataclass(frozen=True)
class SourceInvocation:
    func: Callable
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    name: str

    def resources(self):
        resources = self.func(*self.args, **self.kwargs)
        if isinstance(resources, ResourceInvocation):
            return [resources]
        return list(resources)



def resource(
    name: str | None = None,
    table_name: str | None = None,
    primary_key: str | None = None,
    columns: list[str] | None = None,
    source_name: str | None = None,
):
    def decorator(func: Callable):
        resource_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            return ResourceInvocation(
                func=func,
                args=args,
                kwargs=kwargs,
                name=resource_name,
                table_name=table_name or resource_name,
                primary_key=primary_key,
                columns=list(columns or []),
                source_name=source_name,
            )

        wrapper._etl_resource = {  # type: ignore[attr-defined]
            "name": resource_name,
            "table_name": table_name or resource_name,
            "primary_key": primary_key,
            "columns": list(columns or []),
            "source_name": source_name,
        }
        return wrapper

    return decorator



def source(name: str | None = None):
    def decorator(func: Callable):
        source_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            return SourceInvocation(
                func=func,
                args=args,
                kwargs=kwargs,
                name=source_name,
            )

        wrapper._etl_source = {"name": source_name}  # type: ignore[attr-defined]
        return wrapper

    return decorator
