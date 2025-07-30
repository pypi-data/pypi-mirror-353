"""
http://json-schema.org/latest/json-schema-core.html#anchor8
3.5.  JSON Schema primitive types

JSON Schema defines seven primitive types for JSON values:

    array
        A JSON array.
    boolean
        A JSON boolean.
    integer
        A JSON number without a fraction or exponent part.
    number
        Any JSON number. Number includes integer.
    null
        The JSON null value.
    object
        A JSON object.
    string
        A JSON string.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Callable

import sqlalchemy.types as t
from sqlalchemy import Enum
from sqlalchemy.dialects import postgresql as postgresql_types
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import MapperProperty
from sqlalchemy.orm.base import ONETOMANY
from sqlalchemy.sql.elements import NamedColumn
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.sql.visitors import Visitable

from sqlalchemy_schema.decisions import AbstractDecision, RelationDecision
from sqlalchemy_schema.exceptions import InvalidStatus
from sqlalchemy_schema.types import ColumnPropertyType
from sqlalchemy_schema.walkers import AbstractWalker

Schema = dict[str, Any]

#  tentative
DefaultColumnToSchemaDict = Mapping[type[TypeEngine], str]

default_column_to_schema: DefaultColumnToSchemaDict = {
    t.String: "string",
    t.Text: "string",
    t.Integer: "integer",
    t.SmallInteger: "integer",
    t.BigInteger: "string",  # xxx
    t.Numeric: "integer",
    t.Float: "number",
    t.DateTime: "string",
    t.Date: "string",
    t.Time: "string",  # xxx
    t.LargeBinary: "xxx",
    t.Boolean: "boolean",
    t.Unicode: "string",
    t.ARRAY: "array",
    t.UnicodeText: "string",
    t.Interval: "xxx",
    t.Enum: "string",
    t.LargeBinary: "xxx",
    t.JSON: "object",
    postgresql_types.UUID: "string",
}


# restriction
def string_max_length(column: NamedColumn, sub: dict[str, int], /) -> None:
    if hasattr(column.type, "length") and column.type.length is not None:
        sub["maxLength"] = column.type.length


def enum_one_of(column: NamedColumn[Enum], sub: dict[str, list], /) -> None:
    sub["enum"] = list(column.type.enums)  # type: ignore[attr-defined]


def datetime_format(column: NamedColumn, sub: dict[str, str], /) -> None:
    sub["format"] = "date-time"


def date_format(column: NamedColumn, sub: dict[str, str], /) -> None:
    sub["format"] = "date"


def time_format(column: NamedColumn, sub: dict[str, str], /) -> None:
    sub["format"] = "time"


def uuid_format(column: NamedColumn, sub: dict[str, str], /) -> None:
    sub["format"] = "uuid"


TypeFormatFn = Callable[[NamedColumn, dict[str, Any]], None]
RestrictionDict = Mapping[type[TypeEngine], TypeFormatFn]

default_restriction_dict: RestrictionDict = {
    t.String: string_max_length,
    t.Enum: enum_one_of,
    t.DateTime: datetime_format,
    t.Date: date_format,
    t.Time: time_format,
    postgresql_types.UUID: uuid_format,
}


class Classifier:
    def __init__(
        self,
        mapping: DefaultColumnToSchemaDict = default_column_to_schema,
        /,
        *,
        see_mro: bool = True,
        see_impl: bool = True,
    ) -> None:
        self.mapping = mapping
        self.see_mro = see_mro
        self.see_impl = see_impl

    def __getitem__(self, k: TypeEngine, /) -> tuple[type[TypeEngine], str]:
        cls = k.__class__

        _, mapped = get_class_mapping(
            self.mapping,  # type: ignore[arg-type]
            cls,
            see_mro=self.see_mro,
            see_impl=self.see_impl,
        )

        if mapped is None:
            raise InvalidStatus(f"notfound: {k}. (cls={cls})")

        return cls, mapped  # type: ignore[return-value]


def get_class_mapping(
    mapping: RestrictionDict,
    cls: type[TypeEngine],
    /,
    *,
    see_mro: bool = True,
    see_impl: bool = True,
) -> tuple[DeclarativeMeta | None, TypeFormatFn | None]:
    v = mapping.get(cls)
    if v is not None:
        return cls, v  # type: ignore[return-value]

    # inheritance
    if see_mro:
        for type_ in cls.mro()[1:]:
            if issubclass(TypeEngine, type_):
                break
            if type_ in mapping:
                return [
                    type_,  # type: ignore[return-value]
                    mapping[type_],
                ]

    # decorator's type
    if see_impl and hasattr(cls, "impl"):
        impl = cls.impl
        if not callable(impl):
            # If the class level impl is not a callable (the unusual case),
            impl = impl.__class__
        return get_class_mapping(mapping, impl, see_mro=see_mro, see_impl=see_impl)
    return None, None


DefaultClassfier = Classifier(default_column_to_schema)


def get_children(
    name: str,
    params: Sequence[str] | None,
    /,
    *,
    splitter: str = ".",
    default: list[str] | None = None,
) -> list[str] | None:
    prefix = name + splitter
    if isinstance(params, dict):
        return {k.split(splitter, 1)[1]: v for k, v in params.items() if k.startswith(prefix)}
    elif isinstance(params, (list, tuple)):
        return [e.split(splitter, 1)[1] for e in params if e.startswith(prefix)]
    else:
        return default


pop_marker = object()


class CollectionForOverrides:
    def __init__(self, params: dict[str, Any], /, *, pop_marker: object = pop_marker) -> None:
        self.params = params or {}
        self.not_used_keys = set(params.keys())
        self.pop_marker = pop_marker

    def __contains__(self, k: str, /) -> bool:
        return k in self.params

    def overrides(self, basedict: dict[str, Any], /) -> None:
        for k, v in self.params.items():
            if v == self.pop_marker:
                basedict.pop(k, None)
            else:
                basedict[k] = v
            self.not_used_keys.remove(k)


class ChildFactory:
    def __init__(self, *, splitter: str = ".") -> None:
        self.splitter = splitter

    def default_excludes(self, prop: MapperProperty, /) -> list[str]:
        nullable_excludes = [
            prop.back_populates,
            None if prop.backref is None else prop.backref[0],
        ]
        excludes = [
            nullable_exclude
            for nullable_exclude in nullable_excludes
            if nullable_exclude is not None
        ]

        return excludes

    def child_overrides(self, prop: MapperProperty, overrides: Any, /) -> Any:
        name = prop.key
        children = get_children(name, overrides.params, splitter=self.splitter)
        return overrides.__class__(children, pop_marker=overrides.pop_marker)

    def child_walker(
        self,
        prop: MapperProperty,
        walker: AbstractWalker,
        /,
        *,
        history: Any | None = None,
    ) -> AbstractWalker:
        name = prop.key
        includes = get_children(name, walker.includes, splitter=self.splitter)
        excludes = get_children(name, walker.includes, splitter=self.splitter, default=[])

        if excludes is None:
            excludes = self.default_excludes(prop)
        else:
            excludes.extend(self.default_excludes(prop))

        return walker.clone(
            name,
            prop.mapper,
            includes=includes,
            excludes=excludes,
            history=history,
        )

    def child_schema(
        self,
        prop: MapperProperty,
        schema_factory: SchemaFactory,
        root_schema: dict[str, Any],
        walker: AbstractWalker,
        overrides: Any,
        /,
        *,
        depth: int | None = None,
        history: Any | None = None,
    ) -> dict[str, Any]:
        subschema = schema_factory._build_properties(
            walker,
            root_schema,
            overrides,
            depth=(depth and depth - 1),
            history=history,
            toplevel=False,
        )
        if prop.direction == ONETOMANY:
            return {"type": "array", "items": subschema}
        else:
            return {"type": "object", "properties": subschema}


class SchemaFactory:
    def __init__(
        self,
        walker: type[AbstractWalker],
        /,
        *,
        classifier: Classifier = DefaultClassfier,
        restriction_dict: RestrictionDict = default_restriction_dict,
        child_factory: ChildFactory | None = None,
        relation_decision: AbstractDecision | None = None,
    ) -> None:
        self.classifier = classifier
        self.walker = walker  # class
        self.restriction_set = [{k: v} for k, v in restriction_dict.items()]
        self.child_factory = ChildFactory() if child_factory is None else child_factory
        self.relation_decision = (
            RelationDecision() if relation_decision is None else relation_decision
        )

    def __call__(
        self,
        model: DeclarativeMeta,
        /,
        *,
        includes: Sequence[str] | None = None,
        excludes: Sequence[str] | None = None,
        overrides: dict | None = None,
        depth: int | None = None,
        adjust_required: Callable[[MapperProperty, bool], bool] | None = None,
    ) -> Schema:
        walker = self.walker(model, includes=includes, excludes=excludes)
        overrides_manager = CollectionForOverrides(overrides or {})

        schema: dict[str, Any] = {"title": model.__name__, "type": "object"}
        schema["properties"] = self._build_properties(
            walker, schema, overrides_manager, depth=depth
        )

        if overrides_manager.not_used_keys:
            raise InvalidStatus(f"invalid overrides: {overrides_manager.not_used_keys}")

        if model.__doc__:
            schema["description"] = model.__doc__

        required = self._detect_required(walker, adjust_required=adjust_required)

        if required:
            schema["required"] = required
        return schema

    def _add_items_if_array(
        self, data: dict[str, Any], column: NamedColumn, itype: type[TypeEngine], /
    ) -> None:
        if not isinstance(column.type, t.ARRAY):
            return

        _, item_type = self.classifier[column.type.item_type]

        data["items"] = {"type": item_type}

    def _add_restriction_if_found(
        self, data: dict[str, Any], column: NamedColumn, itype: type[TypeEngine], /
    ) -> None:
        for restriction_dict in self.restriction_set:
            _, fn = get_class_mapping(
                restriction_dict,
                itype,
                see_impl=self.classifier.see_impl,
                see_mro=self.classifier.see_mro,
            )
            if fn is not None:
                if isinstance(fn, (list, tuple)):
                    for f in fn:
                        f(column, data)
                else:
                    fn(column, data)

    def _add_property_with_reference(
        self,
        walker: AbstractWalker,
        root_schema: Schema,
        current_schema: dict[str, Any],
        prop: MapperProperty,
        val: dict[str, Any],
        /,
    ) -> None:
        clsname = prop.mapper.class_.__name__
        if "definitions" not in root_schema:
            root_schema["definitions"] = {}

        if val["type"] == "object":
            current_schema[prop.key] = {"$ref": f"#/definitions/{clsname}"}
            val["required"] = self._detect_required(walker.from_child(prop.mapper))
            root_schema["definitions"][clsname] = val
        else:  # array
            current_schema[prop.key] = {
                "type": "array",
                "items": {"$ref": f"#/definitions/{clsname}"},
            }
            val["type"] = "object"
            val["properties"] = val.pop("items")
            val["required"] = self._detect_required(walker.from_child(prop.mapper))
            root_schema["definitions"][clsname] = val

    def _build_properties(
        self,
        walker: AbstractWalker,
        root_schema: Schema,
        overrides: CollectionForOverrides,
        /,
        *,
        depth: int | None = None,
        history: list[MapperProperty] | None = None,
        toplevel: bool = True,
    ) -> dict[str, Any]:
        definitions: dict[str, Any] = {}

        if depth is not None and depth <= 0:
            return definitions

        if history is None:
            history = []

        for walked_prop in walker.walk():
            for action, prop, opts in self.relation_decision.decision(
                walker, walked_prop, toplevel=toplevel
            ):
                if action == ColumnPropertyType.RELATIONSHIP:  # RelationshipProperty
                    history.append(prop)
                    subwalker = self.child_factory.child_walker(prop, walker, history=history)
                    suboverrides = self.child_factory.child_overrides(prop, overrides)
                    value = self.child_factory.child_schema(
                        prop,
                        self,
                        root_schema,
                        subwalker,
                        suboverrides,
                        depth=depth,
                        history=history,
                    )
                    self._add_property_with_reference(
                        walker, root_schema, definitions, prop, value
                    )
                    history.pop()
                elif action == ColumnPropertyType.FOREIGNKEY:  # ColumnProperty
                    for column in prop.columns:
                        sub = {}
                        if type(column.type) is not Visitable:
                            itype, sub["type"] = self.classifier[column.type]

                            self._add_restriction_if_found(sub, column, itype)
                            self._add_items_if_array(sub, column, itype)

                            if column.doc:
                                sub["description"] = column.doc

                            if overrides is None:
                                raise RuntimeError("overrides is None")

                            if column.name in overrides:
                                overrides.overrides(sub)
                            if opts:
                                sub.update(opts)

                            # Ensure that the column name is a string object
                            # It can be a quoted_name() instance
                            column_name = str(column.name)

                            definitions[column_name] = sub
                        else:
                            raise NotImplementedError
                else:  # immediate
                    definitions[prop.key] = action
        return definitions

    def _detect_required(
        self,
        walker: AbstractWalker,
        /,
        *,
        adjust_required: Callable[[MapperProperty, bool], bool] | None = None,
    ) -> list[str]:
        required_properties_set = set()

        for prop in walker.walk():
            columns = getattr(prop, "columns", {})

            for column in columns:
                required = not column.nullable

                if adjust_required is not None:
                    required = adjust_required(prop, required)
                if required:
                    required_properties_set.add(column.key)

        # Ensure that the column name is a string object
        # It can be a quoted_name() instance
        required_properties = sorted(str(item) for item in required_properties_set)

        return required_properties
