#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Command line utilities.
"""

from abc import ABC, abstractmethod
import sys
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic.v1 import BaseModel, Field
from pydantic_argparse import ArgumentParser


class ActionCommand(ABC, BaseModel):

    @abstractmethod
    def action(self):
        pass


class StringCommand(ActionCommand):

    @staticmethod
    def type(display_str: str):
        class _StringCommand(StringCommand):
            def action(self, file=sys.stdout):
                print(display_str, file=file)
        return _StringCommand


COPYRIGHT_DESCRIPTION = 'print the copyright and exit'
LICENSE_DESCRIPTION = 'print the software license and exit'
VERSION_DESCRIPTION = 'print the version number and exit'


BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


class BaseCli(Generic[BaseModelT]):

    def __init__(self, **extra):
        super().__init__()
        self.args: Optional[BaseModelT] = None
        self.parser: Optional[ArgumentParser] = None
        self.extra: Dict[str, Any] = dict(**extra)

    def run(self):
        self.parser: ArgumentParser = ArgumentParser(model=self.extra.get('model'),
                                                     prog=self.extra.get('prog'),
                                                     description=self.extra.get('description'))
        self.args = self.parser.parse_typed_args()
        self.dispatch()

    def dispatch(self):
        field_names = self.args.__class__.__fields__.keys()
        for field_name in field_names:
            field_value = getattr(self.args, field_name)
            if issubclass(type(field_value), BaseModel):
                func = getattr(self, f'_{field_name}')
                func(field_value)
                break
        else:
            self.parser.error(f'unknown command; expected one of {', '.join(field_names)}')


def at_most_one_from_enum(model_cls, values: Dict[str, Any], enum_cls):
    enum_names = [field_name for field_name, model_field in model_cls.__fields__.items() if model_field.field_info.extra.get('enum') == enum_cls]
    ret = list()
    for field_name in enum_names:
        if values.get(field_name):
            ret.append(field_name)
    if (length := len(ret)) > 1:
        raise ValueError(f'at most one of {', '.join([option_name(enum_name) for enum_name in enum_names])} is allowed, got {', '.join([option_name(enum_name) for enum_name in ret])}')
    return values


def get_from_enum(model_inst, enum_cls, default=None):
    enum_names = [field_name for field_name, model_field in model_inst.__class__.__fields__.items() if model_field.field_info.extra.get('enum') == enum_cls]
    for field_name in enum_names:
        if getattr(model_inst, field_name):
            return enum_cls.from_member(field_name)
    return default


def at_most_one(values: Dict[str, Any], *names: str):
    if (length := _matchy_length(values, *names)) > 1:
        raise ValueError(f'at most one of {', '.join([option_name(name) for name in names])} is allowed, got {length}')
    return values


def exactly_one(values: Dict[str, Any], *names: str):
    if (length := _matchy_length(values, *names)) != 1:
        raise ValueError(f'exactly one of {', '.join([option_name(name) for name in names])} is required, got {length}')
    return values


def one_or_more(values: Dict[str, Any], *names: str):
    if _matchy_length(values, *names) == 0:
        raise ValueError(f'one or more of {', '.join([option_name(name) for name in names])} is required')
    return values


def option_name(name: str):
    return f'{('-' if len(name) == 1 else '--')}{name.replace('_', '-')}'


def _matchy_length(values: Dict[str, Any], *names: str) -> int:
    return len([name for name in names if values.get(name)])
