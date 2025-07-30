# -*- coding: utf-8 -*-
#
# TARGET arch is: __FLAGS__
# WORD_SIZE is: __WORD_SIZE__
# POINTER_SIZE is: __POINTER_SIZE__
# LONGDOUBLE_SIZE is: __LONGDOUBLE_SIZE__
#
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, List, Any, Dict, cast, TypeVar
import functools
import ctypes
import os

F = TypeVar("F", bound=Callable[..., Any])