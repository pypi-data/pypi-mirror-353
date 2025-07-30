from __future__ import annotations

from typing import Iterable

from dynamicprompts.commands import Command
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.sampling_result import SamplingResult
from dynamicprompts.types import CommandList, ResultGen


class CommandCollection:
    """
    A class that holds a collection of commands and manages generating values for them.
    """

    def __init__(self, commands: Iterable[Command], context: SamplingContext) -> None:
        self._commands = list(commands)
        self._generators = [context.generator_from_command(c) for c in self._commands]
        self._values: list[SamplingResult | None] = [next(g) for g in self._generators]

    def get_value(self, command: Command) -> SamplingResult | None:
        try:
            index = self._commands.index(command)
        except ValueError:
            raise ValueError(f"Command {command} not in collection") from None

        generator = self._generators[index]
        value = self._values[index]

        try:
            self._values[index] = next(generator)
        except StopIteration:
            self._values[index] = None
        if self._values[index]:
            # TODO: remove the following safety assert?
            assert isinstance(self._values[index], SamplingResult), "oopsy"
        return value

    @property
    def commands(self) -> CommandList:
        return self._commands

    @property
    def generators(self) -> list[ResultGen]:
        return self._generators
