"""Uncategorised utilities."""
# ruff: noqa: N815
from __future__ import annotations

from http import HTTPStatus
from io import BytesIO
from math import trunc
from os import environ
from pathlib import Path
from shlex import quote
from shutil import copyfile, rmtree, which
from signal import SIGTERM
from typing import TYPE_CHECKING, Literal, NamedTuple, overload, override
import csv
import logging
import os
import re
import sqlite3
import struct
import subprocess as sp
import tarfile
import tempfile
import time

from requests.adapters import BaseAdapter
import platformdirs
import requests
import xz

from .media import CD_FRAMES
from .system import IS_WINDOWS, kill_wine
from .windows import (
    LF_FULLFACESIZE,
    CharacterSet,
    ClipPrecision,
    Family,
    OutputPrecision,
    Pitch,
    Quality,
    Weight,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from paramiko import SFTPClient, SSHClient

    from .typing import StrPath

__all__ = ('WineWindowsVersion', 'add_cdda_times', 'create_wine_prefix', 'secure_move_path')

ZERO_TO_99 = '|'.join(f'{x:02d}' for x in range(100))
ZERO_TO_59 = '|'.join(f'{x:02d}' for x in range(60))
ZERO_TO_74 = '|'.join(f'{x:02d}' for x in range(75))
TIMES_RE = re.compile(f'^({ZERO_TO_99}):({ZERO_TO_59}):({ZERO_TO_74})$')
MAX_MINUTES = 99
MAX_SECONDS = 60
log = logging.getLogger(__name__)


def add_cdda_times(times: Iterable[str] | None) -> str | None:
    """
    Add CDDA time strings and get a total runtime in CDDA format.

    CDDA format is ``MM:SS:FF`` where ``MM`` is minutes, ``SS`` is seconds, and ``FF`` is frames.
    """
    if not times:
        return None
    total_ms = 0
    for time_ in times:
        if not (res := re.match(TIMES_RE, time_)):
            return None
        minutes, seconds, frames = [int(x) for x in res.groups()]
        total_ms += (minutes * MAX_SECONDS * 1000) + (seconds * 1000) + (
            (frames * 1000) // CD_FRAMES)
    minutes = total_ms // (MAX_SECONDS * 1000)
    remainder_ms = total_ms % (MAX_SECONDS * 1000)
    seconds = remainder_ms // 1000
    remainder_ms %= 1000
    frames = round((remainder_ms * 1000 * CD_FRAMES) / 1000000)
    if minutes > MAX_MINUTES or seconds > (MAX_SECONDS - 1) or frames > (CD_FRAMES - 1):
        return None
    return f'{trunc(minutes):02d}:{trunc(seconds):02d}:{trunc(frames):02d}'


WINETRICKS_VERSION_MAPPING = {
    '11': 'win11',
    '10': 'win10',
    'vista': 'vista',
    '2k3': 'win2k3',
    '7': 'win7',
    '8': 'win8',
    'xp': 'winxp',
    '81': 'win81',
    # 32-bit only
    '2k': 'win2k',
    '98': 'win98',
    '95': 'win95'
}
"""Mapping of Windows versions to winetricks versions."""
DEFAULT_DPI = 96
"""Default DPI for Wine prefixes."""
_CREATE_WINE_PREFIX_NOTO_FONT_REPLACEMENTS = {
    'Arial Baltic,186', 'Arial CE,238', 'Arial CYR,204', 'Arial Greek,161', 'Arial TUR,162',
    'Courier New Baltic,186', 'Courier New CE,238', 'Courier New CYR,204', 'Courier New Greek,161',
    'Courier New TUR,162', 'Helv', 'Helvetica', 'MS Shell Dlg', 'MS Shell Dlg 2', 'MS Sans Serif',
    'Segoe UI', 'System', 'Tahoma', 'Times', 'Times New Roman Baltic,186', 'Times New Roman CE,238',
    'Times New Roman CYR,204', 'Times New Roman Greek,161', 'Times New Roman TUR,162', 'Tms Rmn',
    'Verdana'
}
_CREATE_WINE_PREFIX_NOTO_REGISTRY_ENTRIES = {
    'Caption', 'Icon', 'Menu', 'Message', 'SmCaption', 'Status'
}
WineWindowsVersion = Literal['11', '10', 'vista', '2k3', '7', '8', 'xp', '81', '2k', '98', '95']
"""Windows versions supported by Wine."""


class LOGFONTW(NamedTuple):
    """Windows LOGFONTW structure as a named tuple."""
    lfHeight: int
    lfWidth: int
    lfEscapement: int
    lfOrientation: int
    lfWeight: int
    lfItalic: bool
    lfUnderline: bool
    lfStrikeOut: bool
    lfCharSet: int
    lfOutPrecision: int
    lfClipPrecision: int
    lfQuality: int
    lfPitchAndFamily: int


Q4WINE_DEFAULT_ICONS: tuple[tuple[str, str, str, str, str, str], ...] = (
    ('', 'control.exe', 'control', 'Wine control panel', 'system', 'Control Panel'),
    ('', 'eject.exe', 'eject', 'Wine CD eject tool', 'system', 'Eject'),
    ('', 'explorer.exe', 'explorer', 'Browse the files in the virtual Wine Drive', 'system',
     'Explorer'),
    ('', 'iexplore.exe', 'iexplore', 'Wine internet browser', 'system', 'Internet Explorer'),
    ('', 'notepad.exe', 'notepad', 'Wine notepad text editor', 'system', 'Notepad'),
    ('', 'oleview.exe', 'oleview', 'Wine OLE/COM object viewer', 'system', 'OLE Viewer'),
    ('', 'regedit.exe', 'regedit', 'Wine registry editor', 'system', 'Registry Editor'),
    ('', 'taskmgr.exe', 'taskmgr', 'Wine task manager', 'system', 'Task Manager'),
    ('', 'uninstaller.exe', 'uninstaller', 'Uninstall Windows programs under Wine properly',
     'system', 'Uninstaller'),
    ('', 'winecfg.exe', 'winecfg', 'Configure the general settings for Wine', 'system',
     'Configuration'),
    ('', 'wineconsole', 'wineconsole', 'Wineconsole is similar to wine command wcmd', 'system',
     'Console'),
    ('', 'winemine.exe', 'winemine', 'Wine sweeper game', 'system', 'Winemine'),
    ('', 'wordpad.exe', 'wordpad', 'Wine wordpad text editor', 'system', 'WordPad'),
)
"""Shortcuts to add to Q4Wine for the prefix."""


def create_wine_prefix(prefix_name: str,
                       *,
                       _32bit: bool = False,
                       asio: bool = False,
                       disable_explorer: bool = False,
                       disable_services: bool = False,
                       dpi: int = DEFAULT_DPI,
                       dxva_vaapi: bool = False,
                       dxvk_nvapi: bool = False,
                       eax: bool = False,
                       gtk: bool = False,
                       no_associations: bool = False,
                       no_gecko: bool = False,
                       no_mono: bool = False,
                       no_xdg: bool = False,
                       noto_sans: bool = False,
                       prefix_root: StrPath | None = None,
                       sandbox: bool = False,
                       tmpfs: bool = False,
                       tricks: Iterable[str] | None = None,
                       vd: str = 'off',
                       windows_version: WineWindowsVersion = '10',
                       winrt_dark: bool = False) -> Path:
    """
    Create a Wine prefix with custom settings.

    If winetricks is not installed, the ``tricks`` argument will be ignored.

    Parameters
    ----------
    prefix_name : str
        Name of the prefix to create.
    _32bit : bool
        Create a 32-bit Wine prefix.
    asio : bool
        Enable ASIO support.
    disable_explorer : bool
        Disable ``explorer.exe`` from automatically starting.
    disable_services : bool
        Disable ``services.exe`` from automatically starting.
    dpi : int
        Screen DPI.
    dxva_vaapi : bool
        Enable VAAPI support for DXVA.
    dxvk_nvapi : bool
        Enable DXVK NVAPI support.
    eax : bool
        Enable EAX support.
    gtk : bool
        Enable GTK theme support.
    no_associations : bool
        Disable file associations.
    no_gecko : bool
        Disable Gecko support.
    no_mono : bool
        Disable Mono support.
    no_xdg : bool
        Disable XDG support.
    noto_sans : bool
        Use Noto Sans font.
    prefix_root : StrPath | None
        Root directory for the prefix. If ``None``, defaults to ``~/.local/share/wineprefixes``.
    sandbox : bool
        Enable sandbox mode.
    tmpfs : bool
        Use ``/tmp`` as a temporary filesystem.
    tricks : Iterable[str] | None
        List of winetricks to run. If ``None``, defaults to an empty list.
    vd : str
        Virtual desktop mode. If ``'off'``, disables virtual desktop mode.
    windows_version : WineWindowsVersion
        Windows version to set for the prefix.
    winrt_dark : bool
        Enable Windows 10 dark mode.

    Returns
    -------
    Path
        Path to the created prefix.

    Raises
    ------
    FileExistsError
    """
    tricks = list((t for t in tricks
                   if t not in WINETRICKS_VERSION_MAPPING.values() and not t.startswith('vd=')
                   ) if tricks else [])
    prefix_root = Path(prefix_root) if prefix_root else Path.home() / '.local/share/wineprefixes'
    prefix_root.mkdir(parents=True, exist_ok=True)
    target = prefix_root / prefix_name
    if target.exists():
        raise FileExistsError
    arch = 'win32' if _32bit else None
    if 'DISPLAY' not in environ or 'XAUTHORITY' not in environ:
        log.warning('Wine will likely fail to run since DISPLAY or XAUTHORITY are not in the '
                    'environment.')
    esync = environ.get('WINEESYNC', '')
    env = {
        'DISPLAY': environ.get('DISPLAY', ''),
        'PATH': environ['PATH'],
        'WINEPREFIX': str(target),
        'XAUTHORITY': environ.get('XAUTHORITY', ''),
        'WINEDEBUG': environ.get('WINEDEBUG', 'fixme-all')
    } | ({
        'WINEARCH': environ.get('WINEARCH', arch)
    } if arch else {}) | ({
        'WINEESYNC': esync
    } if esync else {})
    # Warm up Wine
    cmd: tuple[str, ...] = ('wineboot', '--init')
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    sp.run(cmd, env=env, check=True)
    # Wait for the server to finish because wineboot does not necessarily quit before the prefix is
    # done being set up.
    cmd = ('wineserver', '-w')
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    sp.run(cmd, env=env, check=True)
    if dpi != DEFAULT_DPI:
        cmd = ('wine', 'reg', 'add', r'HKCU\Control Panel\Desktop', '/t', 'REG_DWORD', '/v',
               'LogPixels', '/d', str(dpi), '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if dxva_vaapi:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DXVA2', '/v', 'backend', '/d', 'va', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if eax:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DirectSound', '/v', 'EAXEnabled', '/d',
               'Y', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if gtk:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine', '/v', 'ThemeEngine', '/d', 'GTK', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if winrt_dark:
        for k in ('AppsUseLightTheme', 'SystemUsesLightTheme'):
            cmd = ('wine', 'reg', 'add',
                   r'HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize', '/t',
                   'REG_DWORD', '/v', k, '/d', '0', '/f')
            log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
            sp.run(cmd, env=env, check=True)
    if no_associations:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\Explorer\FileAssociations', '/v',
               'Enable', '/d', 'N', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if no_xdg:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v',
               'winemenubuilder.exe', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if no_mono:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v', 'mscoree', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if no_gecko:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v', 'mshtml', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if disable_explorer:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v', 'explorer.exe', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if disable_services:
        cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v', 'services.exe', '/f')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
    if tmpfs:
        username = environ.get('USER', environ.get('USERNAME', 'user'))
        rmtree(target / f'drive_c/users/{username}/Temp', ignore_errors=True)
        rmtree(target / 'drive_c/windows/temp', ignore_errors=True)
        Path(target / f'drive_c/users/{username}/Temp').symlink_to(tempfile.gettempdir(),
                                                                   target_is_directory=True)
        Path(target / 'drive_c/windows/temp').symlink_to(tempfile.gettempdir(),
                                                         target_is_directory=True)
    if dxvk_nvapi:
        tricks += ['dxvk']
    try:
        tricks += [WINETRICKS_VERSION_MAPPING[windows_version]]
        if sandbox:
            tricks += ['isolate_home', 'sandbox']
        if vd != 'off':
            tricks += [f'vd={vd}']
        if (winetricks := which('winetricks')):
            cmd = (winetricks, '--force', '--country=US', '--unattended', f'prefix={prefix_name}',
                   *sorted(set(tricks)))
            log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
            sp.run(cmd, check=True)
    except sp.CalledProcessError as e:  # pragma: no cover
        log.warning('Winetricks exit code was %d but it may have succeeded.', e.returncode)
    if dxvk_nvapi:
        cmd = ('setup_vkd3d_proton.sh', 'install')
        log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
        sp.run(cmd, env=env, check=True)
        version = '0.8.3'
        nvidia_libs = 'nvidia-libs'
        prefix = f'{nvidia_libs}-{version}'
        r = requests.get(
            f'https://github.com/SveSop/{nvidia_libs}/releases/download/v{version}/{prefix}.tar.xz',
            timeout=15)
        r.raise_for_status()
        with xz.open(BytesIO(r.content)) as xz_file, tarfile.TarFile(fileobj=xz_file) as tar:
            for item in ('nvcuda', 'nvcuvid', 'nvencodeapi', 'nvapi'):
                cmd = ('wine', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v', item, '/d',
                       'native', '/f')
                log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
                sp.run(cmd, env=env, check=True)
                member = tar.getmember(f'{prefix}/x32/{item}.dll')
                member.name = f'{item}.dll'
                tar.extract(member, target / 'drive_c' / 'windows' / 'syswow64')
            if not _32bit:
                for item in ('nvcuda', 'nvoptix', 'nvcuvid', 'nvencodeapi64', 'nvapi64',
                             'nvofapi64'):
                    cmd = ('wine64', 'reg', 'add', r'HKCU\Software\Wine\DllOverrides', '/v', item,
                           '/d', 'native', '/f')
                    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
                    sp.run(cmd, env=env, check=True)
                    member = tar.getmember(f'{prefix}/x64/{item}.dll')
                    member.name = f'{item}.dll'
                    tar.extract(member, target / 'drive_c' / 'windows' / 'system32')
        for prefix in ('', '_'):
            copyfile(f'/lib64/nvidia/wine/{prefix}nvngx.dll',
                     target / 'drive_c' / 'windows' / 'system32' / f'{prefix}nvngx.dll')
        if not _32bit:
            cmd = ('wine64', 'reg', 'add', r'HKLM\Software\NVIDIA Corporation\Global\NGXCore', '/t',
                   'REG_SZ', '/v', 'FullPath', '/d', r'C:\Windows\system32', '/f')
            log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
            sp.run(cmd, env=env, check=True)
    if noto_sans:
        for font_name in _CREATE_WINE_PREFIX_NOTO_FONT_REPLACEMENTS:
            cmd = ('wine', 'reg', 'add',
                   r'HKLM\Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes', '/t',
                   'REG_SZ', '/v', font_name, '/d', 'Noto Sans', '/f')
            log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
            sp.run(cmd, env=env, check=True)
        face_name = 'Noto Sans'.encode('utf-16le').ljust(LF_FULLFACESIZE, b'\0')
        for entry_name in _CREATE_WINE_PREFIX_NOTO_REGISTRY_ENTRIES:
            cmd = (
                'wine',
                'reg',
                'add',
                r'HKCU\Control Panel\Desktop\WindowMetrics',
                '/t',
                'REG_BINARY',
                '/v',
                f'{entry_name}Font',
                '/d',
                ''.join(f'{x:02x}' for x in struct.pack(
                    '=5l8B64B',
                    *LOGFONTW(
                        lfHeight=-12,  # Size 9 pt
                        lfWidth=0,
                        lfEscapement=0,
                        lfOrientation=0,
                        lfWeight=Weight.FW_BOLD if entry_name == 'Caption' else Weight.FW_NORMAL,
                        lfItalic=False,
                        lfUnderline=False,
                        lfStrikeOut=False,
                        lfCharSet=CharacterSet.DEFAULT_CHARSET,
                        lfOutPrecision=OutputPrecision.OUT_DEFAULT_PRECIS,
                        lfClipPrecision=ClipPrecision.CLIP_DEFAULT_PRECIS,
                        lfQuality=Quality.DEFAULT_QUALITY,
                        lfPitchAndFamily=Pitch.VARIABLE_PITCH | Family.FF_SWISS),
                    *face_name)),
                '/f')
            log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
            sp.run(cmd, env=env, check=True)
    if asio:
        if register := which('wineasio-register'):
            log.debug('Running: %s', register)
            sp.run((register,), env=env, check=True)
        else:
            log.warning('Skipping ASIO setup because wineasio-register is not in PATH.')
    if (db_path := (platformdirs.user_config_path() / 'q4wine/db/generic.dat')).exists():
        # Based on addPrefix() and createPrefixDBStructure().
        # https://github.com/brezerk/q4wine/blob/master/src/core/database/prefix.cpp#L250
        # https://github.com/brezerk/q4wine/blob/master/src/q4wine-lib/q4wine-lib.cpp#L1920
        log.debug('Adding this prefix to Q4Wine.')
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(
                'INSERT INTO prefix (name, path, mountpoint_windrive, run_string, version_id) '
                'VALUES (?, ?, ?, ?, 1)',
                (prefix_name, str(target), 'D:',
                 r'%CONSOLE_BIN% %CONSOLE_ARGS% %ENV_BIN% %ENV_ARGS% /bin/sh -c '
                 r'"%WORK_DIR% %SET_NICE% %WINE_BIN% %VIRTUAL_DESKTOP% %PROGRAM_BIN% '
                 r'%PROGRAM_ARGS% 2>&1 "'))
            prefix_id = c.lastrowid
            log.debug('Q4Wine prefix ID: %d', prefix_id)
            assert prefix_id is not None
            for dir_name in ('system', 'autostart', 'import'):
                c.execute('INSERT INTO dir (name, prefix_id) VALUES (?, ?)', (dir_name, prefix_id))
            for args, exec_, icon_path, desc, folder, display_name in Q4WINE_DEFAULT_ICONS:
                c.execute(
                    """INSERT INTO icon (
    cmdargs, exec, icon_path, desc, dir_id, name, prefix_id, nice)
    VALUES (
        ?, ?, ?, ?, (
            SELECT id FROM dir WHERE name = ? AND prefix_id = ?
        ), ?, ?, 0
    )""", (args or None, exec_, icon_path, desc, folder, prefix_id, display_name, prefix_id))
            c.execute('DELETE FROM logging WHERE prefix_id = ?', (prefix_id,))
    return target


def unregister_wine_file_associations(*, debug: bool = False) -> None:
    """Unregister all Wine file associations."""
    kill_wine()
    for item in (Path.home() / '.local/share/applications').glob('wine-extension-*.desktop'):
        log.debug('Removing file association "%s".', item)
        item.unlink()
    for item in (Path.home() / '.local/share/icons/hicolor').rglob('application-x-wine-extension*'):
        log.debug('Removing icon "%s".', item)
        item.unlink()
    (Path.home() / '.local/share/applications/mimeinfo.cache').unlink(missing_ok=True)
    for item in (Path.home() / '.local/share/mime/packages').glob('x-wine*'):
        log.debug('Removing MIME file "%s".', item)
        item.unlink()
    for item in (Path.home() / '.local/share/application').glob('x-wine-extension*'):
        log.debug('Removing MIME file "%s".', item)
        item.unlink()
    cmd: tuple[str, ...] = ('update-desktop-database', *(('-v',) if debug else ()),
                            str(Path.home() / '.local/share/applications'))
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    sp.run(cmd, check=True)
    cmd = ('update-mime-database', *(('-v',) if debug else
                                     ()), str(Path.home() / '.local/share/mime'))
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    sp.run(cmd, check=True)


def secure_move_path(client: SSHClient,
                     filename: StrPath,
                     remote_target: str,
                     *,
                     dry_run: bool = False,
                     preserve_stats: bool = False,
                     write_into: bool = False) -> None:
    """Like ``scp`` but moves the file."""
    log.debug('Source: "%s", remote target: "%s"', filename, remote_target)

    def mkdir_ignore_existing(sftp: SFTPClient, td: str, times: tuple[float, float]) -> None:
        if not write_into:
            log.debug('MKDIR "%s"', td)
            if not dry_run:
                sftp.mkdir(td)
                if preserve_stats:
                    sftp.utime(td, times)
            return
        try:
            sftp.stat(td)
        except FileNotFoundError:
            log.debug('MKDIR "%s"', td)
            if not dry_run:
                sftp.mkdir(td)
                if preserve_stats:
                    sftp.utime(td, times)

    path = Path(filename)
    _, stdout, __ = client.exec_command('echo "${HOME}"')
    remote_target = remote_target.replace('~', stdout.read().decode().strip())
    with client.open_sftp() as sftp:
        if path.is_file():
            if not dry_run:
                sftp.put(filename, remote_target)
                if preserve_stats:
                    local_s = Path(filename).stat()
                    sftp.utime(remote_target, (local_s.st_atime, local_s.st_mtime))
            log.debug('Deleting local file "%s".', path)
            if not dry_run:
                path.unlink()
        else:
            pf = Path(filename)
            pf_stat = pf.stat()
            bn_filename = pf.name
            dn_prefix = str(pf).replace(bn_filename, '')
            mkdir_ignore_existing(sftp, remote_target, (pf_stat.st_atime, pf_stat.st_mtime))
            for root, dirs, files in os.walk(filename, followlinks=True):
                p_root = Path(root)
                remote_target_dir = f'{remote_target}/{bn_filename}'
                p_root_stat = p_root.stat()
                mkdir_ignore_existing(sftp, remote_target_dir,
                                      (p_root_stat.st_atime, p_root_stat.st_mtime))
                for name in sorted(dirs):
                    p_root_stat = (p_root / name).stat()
                    dp = str(p_root / name).replace(dn_prefix, '')
                    remote_target_dir = f'{remote_target}/{dp}'
                    mkdir_ignore_existing(sftp, remote_target_dir,
                                          (p_root_stat.st_atime, p_root_stat.st_mtime))
                for name in sorted(files):
                    src = p_root / name
                    dp = str(p_root / name).replace(dn_prefix, '')
                    log.debug('PUT "%s" "%s/%s"', src, remote_target, dp)
                    if not dry_run:
                        sftp.put(src, f'{remote_target}/{dp}')
                        if preserve_stats:
                            local_s = Path(src).stat()
                            sftp.utime(f'{remote_target}/{dp}',
                                       (local_s.st_atime, local_s.st_mtime))
            if not dry_run:
                rmtree(filename, ignore_errors=True)
            else:
                log.debug('Would delete local directory "%s".', filename)


@overload
def kill_processes_by_name(name: str) -> None:  # pragma: no cover
    pass


@overload
def kill_processes_by_name(name: str,
                           wait_timeout: float,
                           signal: int = SIGTERM,
                           *,
                           force: bool = False) -> list[int]:  # pragma: no cover
    pass


def kill_processes_by_name(name: str,
                           wait_timeout: float | None = None,
                           signal: int = SIGTERM,
                           *,
                           force: bool = False) -> list[int] | None:
    """
    Terminate processes by name.

    Alternative to using `psutil <https://pypi.org/project/psutil/>`_.

    Parameters
    ----------
    name : str
        Process name (base name) or image name (Windows).
    wait_timeout : float | None
        If set and processes remain after ending processes, wait this amount of time in seconds.
    signal : int
        Signal to use. Only applies to non-Windows.
    force : bool
        If ``wait_timeout`` is set and ``True``, forcefully end the processes after the wait time.

    Returns
    -------
    list[int] | None
        PIDs of processes that may still be running, or ``None`` if ``wait_timeout`` is not
        specified.
    """
    name = f'{name}{Path(name).suffix or ".exe"}' if IS_WINDOWS else name
    pids: list[int] = []
    if IS_WINDOWS:
        sp.run(('taskkill.exe', '/im', name), check=False, capture_output=True)
    else:
        sp.run(('killall', f'-{signal}', name), check=False, capture_output=True)
    if wait_timeout:
        lines = sp.run(
            ('tasklist.exe', '/fo', 'csv', '/fi', f'IMAGENAME eq {name}') if IS_WINDOWS else
            ('ps', 'ax'),
            check=True,
            capture_output=True,
            text=True).stdout.splitlines()
        if pids := [int(x[1]) for x in list(csv.reader(lines))[1:]] if IS_WINDOWS else [
                int(y[0]) for y in (x.split() for x in lines) if Path(y[0]).name == name
        ]:
            time.sleep(wait_timeout)
            if force:
                sp.run(('taskkill.exe', *(t for sl in (('/pid', str(pid)) for pid in pids)
                                          for t in sl), '/f') if IS_WINDOWS else
                       ('kill', '-9', *(str(x) for x in pids)),
                       check=False,
                       capture_output=True)
    return pids if wait_timeout else None


class DataAdapter(BaseAdapter):
    """
    Adapter for requests to handle data: URLs.

    Example use:

    .. code-block:: python
       s = requests.Session()
       s.mount('data:', DataAdapter())
    """
    @override
    def send(self,
             request: requests.PreparedRequest,
             stream: bool = False,
             timeout: float | tuple[float, float] | tuple[float, None] | None = None,
             verify: bool | str = True,
             cert: bytes | str | tuple[bytes | str, bytes | str] | None = None,
             proxies: Mapping[str, str] | None = None) -> requests.Response:
        r = requests.Response()
        assert request.url is not None
        r._content = request.url[5:].encode()  # noqa: SLF001
        r.status_code = HTTPStatus.OK
        return r

    @override
    def close(self) -> None:
        pass
