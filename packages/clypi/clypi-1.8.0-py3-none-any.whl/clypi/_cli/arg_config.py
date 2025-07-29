import typing as t
from dataclasses import asdict, dataclass

from clypi import _type_util
from clypi._cli import arg_parser
from clypi._exceptions import ClypiException
from clypi._prompts import MAX_ATTEMPTS
from clypi._util import UNSET, Unset
from clypi.parsers import Parser

T = t.TypeVar("T")

Nargs: t.TypeAlias = t.Literal["*"] | float


def _get_nargs(_type: t.Any) -> Nargs:
    if _type is bool:
        return 0

    if _type_util.is_list(_type):
        return "*"

    if _type_util.is_union(_type):
        nargs = [_get_nargs(t) for t in _type_util.union_inner(_type)]
        if "*" in nargs:
            return "*"
        return max(t.cast(list[int], nargs))

    return 1


@dataclass
class PartialConfig(t.Generic[T]):
    parser: Parser[T] | None = None
    default: T | Unset = UNSET
    default_factory: t.Callable[[], T] | Unset = UNSET
    help: str | None = None
    short: str | None = None
    prompt: str | None = None
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS
    inherited: bool = False
    hidden: bool = False
    group: str | None = None
    negative: str | None = None
    defer: bool = False
    env: str | None = None


@dataclass
class Config(t.Generic[T]):
    name: str
    parser: Parser[T]
    arg_type: t.Any
    default: T | Unset = UNSET
    default_factory: t.Callable[[], T] | Unset = UNSET
    help: str | None = None
    short: str | None = None
    prompt: str | None = None
    hide_input: bool = False
    max_attempts: int = MAX_ATTEMPTS
    inherited: bool = False
    hidden: bool = False
    group: str | None = None
    negative: str | None = None
    defer: bool = False
    env: str | None = None

    def __post_init__(self):
        if self.is_positional and self.short:
            raise ClypiException("Positional arguments cannot have short names")
        if self.is_positional and self.group:
            raise ClypiException("Positional arguments cannot belong to groups")

    def has_default(self) -> bool:
        return not isinstance(self.default, Unset) or not isinstance(
            self.default_factory, Unset
        )

    def get_default(self) -> T:
        val = self.get_default_or_missing()
        if isinstance(val, Unset):
            raise ValueError(f"Field {self} has no default value!")
        return val

    def get_default_or_missing(self) -> T | Unset:
        if not isinstance(self.default, Unset):
            return self.default
        if not isinstance(self.default_factory, Unset):
            return self.default_factory()
        return UNSET

    @classmethod
    def from_partial(
        cls,
        partial: PartialConfig[T],
        name: str,
        parser: Parser[T] | None,
        arg_type: t.Any,
    ):
        kwargs = asdict(partial)
        kwargs.update(name=name, parser=parser, arg_type=arg_type)
        return cls(**kwargs)

    @property
    def display_name(self):
        name = arg_parser.snake_to_dash(self.name)
        if self.is_opt:
            return f"--{name}"
        return name

    @property
    def negative_name(self):
        assert self.is_opt, "negative_name can only be used for options"
        assert self.negative, "negative is not set"
        negative_name = arg_parser.snake_to_dash(self.negative)
        return f"--{negative_name}"

    @property
    def short_display_name(self):
        assert self.short, f"Expected short to be set in {self}"
        name = arg_parser.snake_to_dash(self.short)
        return f"-{name}"

    @property
    def is_positional(self) -> bool:
        if t.get_origin(self.arg_type) != t.Annotated:
            return False

        metadata = self.arg_type.__metadata__
        for m in metadata:
            if isinstance(m, _Positional):
                return True

        return False

    @property
    def is_opt(self) -> bool:
        return not self.is_positional

    @property
    def nargs(self) -> Nargs:
        return _get_nargs(self.arg_type)

    @property
    def modifier(self) -> str:
        nargs = self.nargs
        if nargs in ("+", "*"):
            return "…"
        elif isinstance(nargs, int) and nargs > 1:
            return "…"
        return ""


def arg(
    default: T | Unset = UNSET,
    parser: Parser[T] | None = None,
    default_factory: t.Callable[[], T] | Unset = UNSET,
    help: str | None = None,
    short: str | None = None,
    prompt: str | None = None,
    hide_input: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
    inherited: bool = False,
    hidden: bool = False,
    group: str | None = None,
    negative: str | None = None,
    defer: bool = False,
    env: str | None = None,
) -> T:
    return PartialConfig(
        default=default,
        parser=parser,
        default_factory=default_factory,
        help=help,
        short=short,
        prompt=prompt,
        hide_input=hide_input,
        max_attempts=max_attempts,
        inherited=inherited,
        hidden=hidden,
        group=group,
        negative=negative,
        defer=defer,
        env=env,
    )  # type: ignore


@dataclass
class _Positional:
    pass


P = t.TypeVar("P")
Positional: t.TypeAlias = t.Annotated[P, _Positional()]
