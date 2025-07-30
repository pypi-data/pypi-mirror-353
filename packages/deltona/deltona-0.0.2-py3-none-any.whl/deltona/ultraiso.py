"""UltraISO wrapper."""
from __future__ import annotations

from pathlib import Path
from shlex import quote
from shutil import copyfile
from typing import TYPE_CHECKING, Literal
import logging
import os
import subprocess as sp

from .string import unix_path_to_wine as base_unix_path_to_wine
from .system import IS_WINDOWS

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .typing import StrPath, StrPathMustExist

__all__ = ('run_ultraiso',)

DEFAULT_WINE_PREFIX = Path.home() / '.local/share/wineprefixes/ultraiso'
MIN_ARGUMENTS = 4 if not IS_WINDOWS else 3
log = logging.getLogger(__name__)


def unix_path_to_wine(s: StrPath) -> str:
    if IS_WINDOWS:
        return str(s)
    return base_unix_path_to_wine(str(s))


def get_ultraiso_path(prefix: StrPath) -> StrPath | None:
    program_files_paths = [f'Program Files{x}/UltraISO/UltraISO.exe' for x in ('', ' (x86)')]
    prefix = Path(prefix) / 'drive_c' if not IS_WINDOWS else Path('C:/')
    for exe in (prefix / x for x in program_files_paths):
        if exe.exists():
            return exe
    return None


class InsufficientArguments(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__('Insufficient amount of arguments.')


def run_ultraiso(
        *,
        add_dirs: Iterable[StrPathMustExist] | None = None,
        add_files: Iterable[StrPathMustExist] | None = None,
        cmd: StrPathMustExist | None = None,
        input: StrPathMustExist | None = None,  # noqa: A002
        output: StrPath | None = None,
        appid: str | None = None,
        preparer: str | None = None,
        publisher: str | None = None,
        sysid: str | None = None,
        volset: int | None = None,
        volume: str | None = None,
        ilong: bool = False,
        imax: bool = False,
        lowercase: bool = False,
        vernum: bool = False,
        hfs: bool = False,
        jlong: bool = False,
        joliet: bool = False,
        rockridge: bool = False,
        udf: bool = False,
        udfdvd: bool = False,
        bootfile: StrPathMustExist | None = None,
        bootinfotable: bool = False,
        optimize: bool = False,
        chdir: str | None = None,
        newdir: str | None = None,
        rmdir: str | None = None,
        ahide: str | None = None,
        hide: str | None = None,
        pn: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9] | None = None,
        bin2iso: StrPathMustExist | None = None,
        dmg2iso: StrPathMustExist | None = None,
        bin2isz: StrPathMustExist | None = None,
        compress: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] | None = None,
        encrypt: Literal[1, 2, 3] | None = None,
        password: str | None = None,
        split: int | None = None,
        extract: StrPath | None = None,
        get: str | None = None,
        list_: StrPath | None = None,
        prefix: StrPathMustExist = DEFAULT_WINE_PREFIX) -> None:
    r"""
    Run UltraISO in a convenient way.

    Despite always passing ``-silent`` to the application, windows including ones requiring
    interaction may still appear.

    On non-Windows, for any option taking a file path, only pass UNIX file paths. They will be
    converted as needed.

    Parameters
    ----------
    input : StrPathMustExist | None
        Input image.
    output : StrPath | None
        Output image.
    add_dirs : Iterable[StrPath] | None
        Directories to add.
    add_files : Iterable[StrPath] | None
        Files to add.
    cmd : StrPathMustExist | None
        File to read command line arguments from. If this argument is present and not ``None``, all
        other arguments are ignored.
    appid : str | None
        Application ID.
    preparer : str | None
        Preparer name.
    publisher : str | None
        Publisher name.
    sysid : str | None
        System ID.
    volset : int | None
        Volume set ID.
    volume : str | None
        Volume label.
    ilong : bool
        Long filename for ISO 9660 volume, up to 31 characters.
    imax : bool
        Max filename for ISO 9660 volume, up to 207 characters.
    lowercase : bool
        Allow lowercase letters.
    vernum : bool
        Include file version number.
    hfs : bool
        Create Apple HFS volume.
    jlong : bool
        Long filenames for joliet volume, up to 103 characters.
    joliet : bool
        Create a Joliet volume.
    rockridge : bool
        Create RockRidge volume.
    udf : bool
        Create UDF volume.
    udfdvd : bool
        Create UDF DVD image (this option will overwrite all other volume settings).
    bootfile : StrPathMustExist | None
        Boot file.
    bootinfotable : bool
        Generate boot information table in boot file.
    optimize : bool
        Optimize file systems by coding same files only once.
    chdir : str | None
        Change current directory in ISO image.
    newdir : str | None
        Create a new directory.
    rmdir : str | None
        Remove a file or folder from ISO image (full path should be specified).
    ahide : str | None
        Set advanced hidden attribute of a file or folder (full path should be specified).
    hide : str | None
        Set hidden attribute of a file or folder (full path should be specified).
    pn : Literal[1, 2, 3, 4, 5, 6, 7, 8, 9] | None
        Set priority of a file or folder(full path should be specified).
    bin2iso : StrPathMustExist | None
        Convert input CD/DVD image to ISO format.
    dmg2iso : StrPathMustExist | None
        Convert input DMG image to ISO format.
    bin2isz : StrPathMustExist | None
        Convert image to ISZ.
    compress : Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] | None
        Set compression level.
    encrypt : Literal[1, 2, 3] | None
        Set encryption method.
    password : str | None
        Set password.
    split : int | None
        Set segment size in bytes.
    extract : StrPath | None
        Extract ISO image to specified directory.
    get : str | None
        Set a file or directory (full path) to be extracted.
    list\_ : StrPath | None
        Create a list of files and directores in an ISO image.

    Raises
    ------
    InsufficientArguments
        If not enough arguments are passed.
    FileNotFoundError
        If the UltraISO executable cannot be found.
    """  # noqa: DOC501
    if (actual_exe_path := get_ultraiso_path(prefix)) is None:
        raise FileNotFoundError
    env = {}
    if not IS_WINDOWS:
        env = {'WINEPREFIX': str(prefix), 'HOME': os.environ['HOME']}
        if 'DISPLAY' not in os.environ or 'XAUTHORITY' not in os.environ:
            log.warning(
                'UltraISO.exe will likely fail to run since DISPLAY or XAUTHORITY are not in the '
                'environment.')
        env['DISPLAY'] = os.environ.get('DISPLAY', '')
        env['XAUTHORITY'] = os.environ.get('XAUTHORITY', '')
        env['WINEDEBUG'] = 'fixme-all'
    sp_args: list[str] = ['wine'] if not IS_WINDOWS else []
    sp_args += [str(actual_exe_path), '-silent']
    if cmd:
        sp_args += ['-cmd', unix_path_to_wine(cmd)]
    else:
        for key, filename in (('-in', input), ('-out', output)):
            if filename:
                sp_args += [key, unix_path_to_wine(filename)]
        for file in (add_files or []):
            sp_args += ['-file', unix_path_to_wine(file)]
        for dir_ in (add_dirs or []):
            sp_args += ['-directory', str(dir_)]
        for k in (k for k, v in {
                'bootinfotable': bootinfotable,
                'hfs': hfs,
                'ilong': ilong,
                'imax': imax,
                'jlong': jlong,
                'joliet': joliet,
                'lowercase': lowercase,
                'optimize': optimize,
                'rockridge': rockridge,
                'udf': udf,
                'udfdvd': udfdvd,
                'vernum': vernum
        }.items() if v):
            sp_args += [f'-{k}']
        for k, v in ((k, v) for k, v in {
                'bootfile': bootfile,
                'bin2iso': bin2iso,
                'dmg2iso': dmg2iso,
                'bin2isz': bin2isz
        }.items() if v is not None):
            sp_args += [f'-{k}', unix_path_to_wine(v)]
        for k, v in ((k, v) for k, v in {
                'appid': appid,
                'preparer': preparer,
                'publisher': publisher,
                'sysid': sysid,
                'volume': volume,
                'chdir': chdir,
                'newdir': newdir,
                'rmdir': rmdir,
                'ahide': ahide,
                'hide': hide,
                'password': password,
                'extract': extract,
                'get': get,
                'list': list_
        }.items() if v is not None):
            sp_args += [f'-{k}', str(v)]
        for k, i in ((k, i) for k, i in {
                'volset': volset,
                'compress': compress,
                'encrypt': encrypt,
                'split': split,
                'pn': pn
        }.items() if i is not None):
            sp_args += [f'-{k}', str(i)]
    if len(sp_args) < MIN_ARGUMENTS:
        raise InsufficientArguments
    quoted_args = ' '.join(quote(x) for x in sp_args)
    if not IS_WINDOWS:
        log.debug('Command: env %s %s', quote(f'WINEPREFIX={prefix}'), quoted_args)
    else:
        log.debug('Command: %s', quoted_args)
    try:
        sp.run(sp_args, env=env, check=True)
    except sp.CalledProcessError as e:
        if stderr := e.stderr.strip():
            log.exception('stderr output:')
            for line in stderr.splitlines():
                if (not IS_WINDOWS and ('winemenubuilder.exe' in line or 'fixme:' in line
                                        or 'wine: using fast synchronization.' in line)):
                    continue
                log.exception(' -> %s', line)
        raise


ULTRAISO_FONT_REPLACEMENT_MAX_LENGTH = 13


class InvalidExec(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__('Font not found in file. This is not the original UltraISO executable.')


def patch_ultraiso_font(exe: os.PathLike[str], font_name: str = 'Noto Sans') -> None:
    """
    Patch hard-coded UI font in UltraISO executable.

    Must use the original executable. This will use a backup file if present if it has the suffix
    ``.exebak``.

    Raises
    ------
    ValueError
        If the font name is too long.
    FileNotFoundError
        If the executable does not exist.
    IsADirectoryError
        If the executable is a directory.
    InvalidExec
        If the executable is not the original UltraISO executable.
    """
    exe = Path(exe)
    if len(font_name) > ULTRAISO_FONT_REPLACEMENT_MAX_LENGTH:
        msg = f'Font name too long. Max length is {ULTRAISO_FONT_REPLACEMENT_MAX_LENGTH}.'
        raise ValueError(msg)
    if not exe.exists():
        msg = f'File {exe} does not exist.'
        raise FileNotFoundError(msg)
    if not exe.is_file():
        msg = f'File {exe} is a directory.'
        raise IsADirectoryError(msg)
    backup_file = exe.with_suffix('.exebak')
    if backup_file.exists():
        if not backup_file.is_file():
            msg = f'File {backup_file} is a directory.'
            raise IsADirectoryError(msg)
    else:
        copyfile(exe, exe.with_suffix('.exebak'))
    data = backup_file.read_bytes()
    if b'MS Sans Serif\x00' not in data:
        raise InvalidExec
    exe.write_bytes(data.replace(b'MS Sans Serif\x00', font_name.encode() + b'\x00'))
