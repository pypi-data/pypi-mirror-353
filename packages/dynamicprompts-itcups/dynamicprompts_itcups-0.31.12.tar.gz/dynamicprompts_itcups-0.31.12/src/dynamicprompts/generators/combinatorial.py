from __future__ import annotations

import logging

from dynamicprompts import constants
from dynamicprompts.enums import SamplingMethod
from dynamicprompts.generators.promptgenerator import PromptGenerator
from dynamicprompts.parser.config import ParserConfig, default_parser_config
from dynamicprompts.sampling_context import SamplingContext
from dynamicprompts.wildcards import WildcardManager

logger = logging.getLogger(__name__)


class CombinatorialPromptGenerator(PromptGenerator):
    def __init__(
        self,
        wildcard_manager: WildcardManager | None = None,
        ignore_whitespace: bool = False,
        clean_prompts: bool = False,
        clean_not_found_wildcards: bool = False,
        parser_config: ParserConfig = default_parser_config,
    ) -> None:
        wildcard_manager = wildcard_manager or WildcardManager()
        self._context = SamplingContext(
            wildcard_manager=wildcard_manager,
            default_sampling_method=SamplingMethod.COMBINATORIAL,
            ignore_whitespace=ignore_whitespace,
            clean_prompts = clean_prompts,
            clean_not_found_wildcards = clean_not_found_wildcards,
            parser_config=parser_config,
        )

    def generate(
        self,
        template: str | None,
        max_prompts: int | None = constants.MAX_IMAGES,
        **kwargs,
    ) -> list[str]:
        prompts = [
            str(p) for p in self._context.sample_prompts((template or ""), max_prompts)
        ]
        if self._context.clean_prompts:
            prompts = self.clean_prompts(prompts)
        return prompts
