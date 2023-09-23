from abc import ABC
from dataclasses import dataclass
from typing import Literal as LiteralType, Optional


class Term(ABC):
    pass


class MyLangType(ABC):
    pass


BinOpName = LiteralType["add", "sub", "mul", "div", "mod", "gt", "lt", "ge", "le", "eq"]


@dataclass
class IntType(MyLangType):
    size = 64


@dataclass
class BoolType(MyLangType):
    size = 8


@dataclass
class NullType(MyLangType):
    pass

@dataclass
class Parameter:
    name: str
    value_type: MyLangType

@dataclass
class FunctionType(MyLangType):
    parameters: list[Parameter]
    return_type: MyLangType
    closure_parameters: Optional[list[Parameter]] = None


@dataclass
class LiteralValue(Term):
    value_type: MyLangType
    value: int | bool | None


@dataclass
class VariableDeclaration(Term):
    name: str
    value_type: MyLangType
    value: Term


@dataclass
class Store(Term):
    name: str
    value: Term


@dataclass
class Load(Term):
    name: str


@dataclass
class Operator(Term):
    op: BinOpName
    left: Term
    right: Term


@dataclass
class Body(Term):
    statements: list[Term]


@dataclass
class Function(Term):
    name: str
    parameters: list[Parameter]
    body: Body
    return_type: MyLangType = NullType()

    @property
    def value_type(self) -> FunctionType:
        return FunctionType(
            parameters=[param for param in self.parameters],
            return_type=self.return_type,
        )


@dataclass
class Return(Term):
    value: Term


@dataclass
class Call(Term):
    name: str
    arguments: list[Term]


@dataclass
class If(Term):
    condition: Term
    then: Body
    otherwise: Body | None = None


@dataclass
class Module(Term):
    body: Body
    name: str = "module"
