from pathlib import Path
from typing import Optional

import pytest
from typing_extensions import override

from clypi import Command, Positional, arg
from clypi._cli.arg_parser import Arg


def _raise_error() -> str:
    raise ValueError("Whoops! This should never be called")


class ExampleSubCommand(Command):
    """Some sample docs"""

    positional: Positional[tuple[str | Path, ...]]

    @override
    async def run(self):
        print("subcommand")


class ExampleCommand(Command):
    """
    Some sample documentation for the main command
    """

    flag: bool = False
    subcommand: Optional[ExampleSubCommand] = None
    option: list[str] = arg(
        short="o", help="A list of strings please", default_factory=list
    )
    default_test: str = arg(default_factory=_raise_error)

    @override
    @classmethod
    def prog(cls):
        return "example"

    @override
    @classmethod
    def epilog(cls):
        return "Some text to display after..."

    @override
    async def run(self):
        print("main")


def test_expected_base():
    assert ExampleCommand.help() == "Some sample documentation for the main command"
    assert ExampleCommand.prog() == "example"
    assert ExampleCommand.full_command() == ["example"]
    assert ExampleCommand.epilog() == "Some text to display after..."


def test_expected_options():
    opts = ExampleCommand.options()
    assert len(opts) == 3

    assert opts["flag"].name == "flag"
    assert opts["flag"].arg_type is bool
    assert opts["flag"].nargs == 0

    assert opts["option"].name == "option"
    assert opts["option"].arg_type == list[str]
    assert opts["option"].nargs == "*"


def test_expected_positional():
    pos = ExampleSubCommand.positionals()
    assert len(pos) == 1

    assert pos["positional"].name == "positional"
    assert pos["positional"].arg_type == Positional[tuple[str | Path, ...]]
    assert pos["positional"].nargs == 1


def test_expected_subcommands():
    ec = ExampleCommand.subcommands()
    assert len(ec) == 2

    assert ec[None] is None

    sub = ec["example-sub-command"]
    assert sub is ExampleSubCommand
    assert sub.prog() == "example-sub-command"
    assert sub.help() == "Some sample docs"


def test_expected_cls_introspection():
    assert ExampleCommand.flag is False


def test_expected_init():
    cmd = ExampleCommand(default_test="")
    assert cmd.flag is False
    assert cmd.option == []
    assert cmd.subcommand is None


def test_expected_init_with_kwargs():
    cmd = ExampleCommand(
        flag=True,
        option=["f"],
        subcommand=ExampleSubCommand(positional=tuple("g")),
        default_test="",
    )
    assert cmd.flag is True
    assert cmd.option == ["f"]
    assert cmd.subcommand is not None
    assert cmd.subcommand.positional == tuple("g")


def test_expected_init_with_args():
    cmd = ExampleCommand(True, ExampleSubCommand(tuple("g")), ["f"], "")
    assert cmd.flag is True
    assert cmd.option == ["f"]
    assert cmd.subcommand is not None
    assert cmd.subcommand.positional == tuple("g")


def test_expected_init_with_mixed_args_kwargs():
    cmd = ExampleCommand(
        True, ExampleSubCommand(tuple("g")), option=["f"], default_test=""
    )
    assert cmd.flag is True
    assert cmd.option == ["f"]
    assert cmd.subcommand is not None
    assert cmd.subcommand.positional == tuple("g")


def test_expected_repr():
    cmd = ExampleCommand(
        flag=True,
        option=["f"],
        subcommand=ExampleSubCommand(positional=tuple("g")),
        default_test="foo",
    )
    assert (
        str(cmd)
        == "ExampleCommand(flag=True, option=['f'], subcommand=ExampleSubCommand(positional=('g',)), default_test=foo)"
    )


def test_get_similar_opt_error():
    with pytest.raises(ValueError) as exc_info:
        raise ExampleCommand.get_similar_arg_error(
            Arg(
                "falg",  # codespell:ignore
                "--falg",
                "long-opt",
            )
        )

    assert exc_info.value.args[0] == "Unknown option '--falg'. Did you mean '--flag'?"


def test_get_similar_opt_short_error():
    with pytest.raises(ValueError) as exc_info:
        raise ExampleCommand.get_similar_arg_error(
            Arg(
                "c",  # codespell:ignore
                "-c",
                "short-opt",
            )
        )

    assert exc_info.value.args[0] == "Unknown option '-c'. Did you mean '-o'?"


def test_get_similar_subcmd_error():
    with pytest.raises(ValueError) as exc_info:
        raise ExampleCommand.get_similar_arg_error(
            Arg(
                "example-suv-command",
                "example-suv-command",
                "pos",
            )
        )

    assert (
        exc_info.value.args[0]
        == "Unknown argument 'example-suv-command'. Did you mean 'example-sub-command'?"
    )


def test_get_similar_non_similar():
    with pytest.raises(ValueError) as exc_info:
        raise ExampleCommand.get_similar_arg_error(
            Arg(
                "foo",
                "foo",
                "pos",
            )
        )

    assert exc_info.value.args[0] == "Unknown argument 'foo'"


def test_repeated_subcommands():
    class Example1(Command):
        @override
        @classmethod
        def prog(cls):
            return "example"

    class Example2(Command):
        @override
        @classmethod
        def prog(cls):
            return "example"

    with pytest.raises(TypeError) as exc_info:

        class Main(Command):
            subcommand: Example1 | Example2

    assert exc_info.value.args[0] == "Found duplicate subcommand 'example' in Main"
