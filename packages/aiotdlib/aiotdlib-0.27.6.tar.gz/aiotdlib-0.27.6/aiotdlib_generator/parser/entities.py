from __future__ import annotations

import re
import typing

from pydantic import BaseModel
from pydantic import field_validator
from pydantic import model_validator

from .utils import lower_first
from .utils import snake_case
from .utils import upper_first

vector_type_regex = re.compile(r"[Vv]ector<(?P<type>.*)>")
list_type_regex = re.compile(r".*[Vv]ector\[(?P<type>\w+)].*")
core_types = [
    'int',
    'int32',
    'int53',
    'int64',
    'long',
    'double',
    'float',
    'string',
    'str',
    'bool',
    'bytes',
    'vector'
]


class BaseType(BaseModel):
    name: str

    @property
    def snake_name(self) -> str:
        return snake_case(self.name)

    @property
    def lf_name(self) -> str:
        """
        lf - abbreviation of Lower_First
        """
        return lower_first(self.name)

    @property
    def uf_name(self) -> str:
        """
        uf - abbreviation of Upper_First
        """
        return upper_first(self.name)


class Parameter(BaseModel):
    # Optional constraints
    nullable: bool = False
    default_value: typing.Optional[str] = None
    min_length: typing.Optional[int] = None
    max_length: typing.Optional[int] = None

    type: str
    name: str
    alias: typing.Optional[str] = None
    doc: str = ""

    @field_validator('name')
    @classmethod
    def check_name(cls, name):
        if name in ['json', 'filter', 'type', 'hash', 'class']:
            return f"{name}_"

        return name

    @model_validator(mode='after')
    def assign_alias(self) -> 'Parameter':
        if (alias := self.name.rstrip('_')) in ['json', 'filter', 'type', 'hash']:
            self.alias = alias

        return self

    @field_validator('type', mode="before")
    @classmethod
    def convert_tl_type(cls, tl_type: str) -> str:
        if not tl_type:
            return ""

        if tl_type.lower() in core_types:
            return upper_first(tl_type)

        vector_type_match = vector_type_regex.match(tl_type)

        if vector_type_match:
            return f"Vector[{cls.convert_tl_type(vector_type_match.group('type'))}]"

        return upper_first(tl_type)

    @property
    def has_constraints(self):
        return self.is_core_type and (self.min_length is not None or self.max_length is not None)

    @property
    def is_constructor(self) -> bool:
        return self.import_type is not None

    @property
    def is_vector_type(self) -> bool:
        return "vector" in self.type.lower()

    @property
    def is_core_type(self):
        return self.type.lower() in core_types

    @property
    def doc_type(self) -> str:
        if self.is_vector_type:
            return f":class:`{self.type}`"

        return f":class:`{self.type}`"

    @property
    def import_type(self) -> typing.Optional[str]:
        if self.type.lower() in core_types:
            return None

        if self.is_vector_type:
            inner_vector_type = list_type_regex.match(self.type).group('type')

            if inner_vector_type.lower() in core_types:
                return None

            return inner_vector_type

        return self.type

    @property
    def optional_type(self):
        # Workaround for nullable vector types items https://github.com/tdlib/td/issues/1016#issuecomment-618959102
        if self.is_vector_type:
            return re.sub(r"(.*Vector\[)(\w+)(].*)", r'\1typing.Optional[\2]\3', self.type)

        return f"typing.Optional[{self.type}]"


class Dependency(BaseModel):
    name: str
    type: str

    def __eq__(self, other):
        if not isinstance(other, Dependency):
            return False

        return self.name == other.name and self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return str.__hash__(f"{self.name}.{self.type}")


class BaseEntity(BaseType):
    doc: str = ""
    parameters: list[Parameter] = []

    @property
    def has_shadow_names(self) -> bool:
        return any(p.name[-1] == '_' for p in self.parameters)

    @property
    def is_function(self) -> bool:
        return isinstance(self, Function)

    @property
    def is_constructor(self) -> bool:
        return isinstance(self, ConstructorShort)

    @property
    def dependencies(self) -> list[Dependency]:
        return []


class ConstructorShort(BaseEntity):
    is_abstract: bool = False


class Constructor(ConstructorShort):
    subclasses: list[Constructor] = []
    cross_deps: list[Constructor] = []
    parent_class: typing.Optional[ConstructorShort] = None

    @property
    def has_shadow_names(self) -> bool:
        for s in self.subclasses:
            for p in s.parameters:
                if "_" in p.name:
                    return True

        for cd in self.cross_deps:
            for p in cd.parameters:
                if "_" in p.name:
                    return True

        return super(Constructor, self).has_shadow_names

    @property
    def dependencies(self) -> list[Dependency]:
        deps = set()
        cross_deps = [c.name for c in self.cross_deps]

        for p in self.parameters:
            if bool(p.import_type) and not bool(p.import_type) in cross_deps:
                deps.add(Dependency(name=snake_case(p.import_type), type=p.import_type))

        for subclass in self.subclasses:
            for p in subclass.parameters:
                if (
                        bool(p.import_type)
                        and p.import_type != self.uf_name
                        and upper_first(p.import_type) not in cross_deps
                ):
                    deps.add(
                        Dependency(
                            name=snake_case(p.import_type),
                            type=p.import_type
                        )
                    )

        for dep in self.cross_deps:
            for p in dep.parameters:
                if bool(p.import_type) and p.import_type != self.uf_name:
                    deps.add(
                        Dependency(
                            name=snake_case(p.import_type),
                            type=p.import_type
                        )
                    )

        return list(sorted(deps, key=lambda x: x.name))


class Function(BaseEntity):
    return_type: typing.Union[str, Constructor]

    @field_validator('return_type', mode="before")
    @classmethod
    def _convert_return_type(cls, return_type: typing.Union[str, Constructor]) -> typing.Union[str, Constructor]:
        if not return_type:
            return ""

        if isinstance(return_type, str):
            if return_type.lower() in core_types:
                return upper_first(return_type)
            else:
                raise ValueError

        return return_type

    @property
    def return_type_str(self) -> str:
        return self.return_type if isinstance(self.return_type, str) else self.return_type.uf_name

    @property
    def dependencies(self) -> list[Dependency]:
        deps = set()

        for p in self.parameters:
            if p.import_type is not None:
                deps.add(
                    Dependency(
                        name=snake_case(p.import_type),
                        type=p.import_type
                    )
                )

        return list(sorted(deps, key=lambda x: x.name))


BaseEntity.model_rebuild()
Constructor.model_rebuild()
