from __future__ import annotations

import dataclasses
from typing import Generator, Iterable, List

from dynamicprompts.commands import Command
from dynamicprompts.sampling_result import SamplingResult

ResultGen = Generator[SamplingResult, None, None]
ResultIter = Iterable[SamplingResult]
CommandList = List[Command]
CommandListGen = Generator[CommandList, None, None]
StringIter = Iterable[str]

@dataclasses.dataclass
class PromptMeta:
    collected_text = ""
    
    def reset(self):
        self.collected_text = ""
        
    def __repr__(self):
        return f"{self.collected_text}"

def to_result_gen(values: Iterable[SamplingResult | str]) -> ResultGen:
    for s in values:
        if isinstance(s, SamplingResult):
            yield s
        else:
            assert isinstance(s, str), f"expected str, got {type(s)}"
            yield SamplingResult(text=s)


def to_string_gen(values: Iterable[SamplingResult | str]) -> StringIter:
    for s in values:
        if isinstance(s, SamplingResult):
            yield s.text
        else:
            assert isinstance(s, str), f"expected str, got {type(s)}"
            yield s
