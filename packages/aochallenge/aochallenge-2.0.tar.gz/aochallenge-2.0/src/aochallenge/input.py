#!/usr/bin/python3

import itertools
import os
import sys
from typing import Any


def load(
    splitlines: bool = False,
    splitrecords: str | None = None,
    recordtype: list[type] | tuple[type, ...] | type | None = None,
    *,
    lut: dict[str | None, Any] | None = None,
    filename: str | None = None,
) -> list[str | int | list[str | int]] | Any:
    if filename is None:
        filename = os.path.dirname(sys.argv[0]) + "/input@@"
    variant: str = sys.argv[1] if len(sys.argv) > 1 else ""
    content: Any
    if lut is not None:
        lut_content = lut[variant if variant else None]
        if not isinstance(lut_content, str):
            return lut_content
        content = lut_content
    else:
        filename = filename.replace("@@", variant)
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                content = f.read()
        elif os.path.isfile(filename + ".txt"):
            with open(filename + ".txt", "r") as f:
                content = f.read()
        else:
            raise FileNotFoundError(f"Couldn't load either '{filename}' or '{filename}.txt'")
    if splitlines:
        content = content.splitlines()
        if splitrecords is not None:
            for i, row in enumerate(content):
                if splitrecords == "":
                    content[i] = list(row)
                else:
                    content[i] = row.split(splitrecords)
                if recordtype is not None:
                    content[i] = _convert_records(content[i], recordtype)
        elif recordtype is not None:
            content = _convert_records(content, recordtype)
    elif splitrecords is not None:
        content = content.splitlines()
        if splitrecords == "":
            content = list(content[0])
        else:
            content = content[0].split(splitrecords)
        if recordtype is not None:
            content = _convert_records(content, recordtype)
    return content


def variant() -> str | None:
    return sys.argv[1] if len(sys.argv) > 1 else None


def _convert_records(
    content: str, recordtype: list[type] | tuple[type, ...] | type
) -> list[Any]:
    if callable(recordtype):
        return [recordtype(e) for e in content]
    if type(recordtype) in (list, tuple):
        lastfunc: type | None = str
        newcontent: list[Any] = []
        for data, func in itertools.zip_longest(content, recordtype):
            if func is None:
                func = lastfunc
            else:
                lastfunc = func
            assert func is not None
            newcontent.append(func(data))
    return newcontent
