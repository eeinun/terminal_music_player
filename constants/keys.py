from enum import Enum


__COMMON_KEYS = {
    'SPACE': b' ',
    'Q': b'q',
    'R': b'r',
}

__WINDOWS_SPECIFIC_KEYS = {
    'ESCAPE': b'\xe0',
    'RIGHT': b'\xe0M',
    'LEFT': b'\xe0K',
}

__UNIX_SPECIFIC_KEYS = {
    'ESCAPE': b'\x1b',
    'RIGHT': b'\x1b[C',
    'LEFT': b'\x1b[D',
}


WindowKey = Enum(
    'WindowKey',
    {**__COMMON_KEYS, **__WINDOWS_SPECIFIC_KEYS}
)

UnixKey = Enum(
    'UnixKey',
    {**__COMMON_KEYS, **__UNIX_SPECIFIC_KEYS}
)