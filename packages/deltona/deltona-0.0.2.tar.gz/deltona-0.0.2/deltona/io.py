"""General I/O functions."""
from __future__ import annotations

from binascii import crc32
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from zipfile import ZipFile
import contextlib
import io
import logging
import os
import re
import shutil
import subprocess as sp

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from .typing import StrPath

__all__ = ('RARInfo', 'SFVVerificationError', 'UnRAR', 'UnRARError', 'UnRARExtractionTestFailed',
           'context_os_open', 'extract_gog', 'extract_rar_from_zip', 'make_sfv', 'unpack_0day',
           'unpack_ebook', 'verify_sfv')

log = logging.getLogger(__name__)


@contextlib.contextmanager
def context_os_open(path: StrPath,
                    flags: int,
                    mode: int = 511,
                    *,
                    dir_fd: int | None = None) -> Iterator[int]:
    """
    Context-managed file descriptor opener.

    Parameters
    ----------
    path : str
        Path to open.
    flags : int
        Flags to use when opening the file.
    mode : int
        Mode to use when opening the file.
    dir_fd : int | None
        Directory file descriptor to use when opening the file. Defaults to ``None``.

    Yields
    ------
    int
        File descriptor.
    """
    f = os.open(path, flags, mode, dir_fd=dir_fd)
    yield f
    os.close(f)


def unpack_0day(path: StrPath, *, remove_diz: bool = True) -> None:
    """
    Unpack RAR files from 0day zip file sets.

    Parameters
    ----------
    path : str
        Path where zip files are located.
    remove_diz : bool
        Remove any files matching `*.diz` glob (not case-sensitive). Defaults to ``True``.
    """
    path = Path(path)
    with contextlib.chdir(path):
        for zip_file in path.glob('*.zip'):
            with ZipFile(zip_file) as z:
                z.extractall()
            zip_file.unlink()
        if remove_diz:
            for diz in path.glob('*.[Dd][Ii][Zz]'):
                diz.unlink()
        rars = list(path.glob('*.rar'))
        with Path(re.sub(r'(?:\.part\d+)?\.r(?:[0-9][0-9]|ar)$', '.sfv',
                         rars[0].name.lower())).open('w+', encoding='utf-8') as f:
            f.write(f'; {datetime.now(tz=UTC).astimezone()}\n')
            f.writelines(f'{rar.name} {crc32(rar.read_bytes()):08X}\n' for rar in sorted(
                path.glob('*.part*.rar' if any(
                    re.search(r'\.part[0-9]{,3}\.rar$', str(r), re.IGNORECASE)
                    for r in rars) else '*.[rstuvwxyz][0-9a][0-9r]')))


def extract_rar_from_zip(zip_file: ZipFile) -> Iterator[str]:
    """
    Extract RAR files from a zip file.

    Parameters
    ----------
    zip_file : ZipFile
        The zip file to extract RAR files from.

    Yields
    ------
    str
        The name of the extracted RAR file.
    """
    for x in (x for x in zip_file.namelist() if re.search(r'\.r(?:ar|\d{2})$', x)):
        zip_file.extract(x)
        yield x


def unpack_ebook(path: StrPath) -> None:
    """
    Unpack a specially packed eBook file.

    Parameters
    ----------
    path : str
        Path where the zip files are located.

    Raises
    ------
    ValueError
    NotADirectoryError
    FileExistsError
    """
    def unrar_x(rar: StrPath) -> None:
        sp.run(('unrar', 'x', '-y', str(rar)), capture_output=True, check=True)

    if not (path := Path(path)).is_dir():
        raise NotADirectoryError
    with contextlib.chdir(path):
        zip_listing = frozenset(ZipFile(x) for x in path.iterdir() if x.name.endswith('.zip'))
        if len(zip_listing) == 0:
            raise FileExistsError
        extracted = [Path(x) for y in (extract_rar_from_zip(z) for z in zip_listing) for x in y]
        rar = next((x for x in extracted if x.name.endswith('.rar')), None)
        if not rar:
            raise ValueError(0)
        # Only need the .rar
        unrar_x(rar)
        epub_list = [Path(x) for x in path.iterdir() if x.name.lower().endswith('.epub')]
        pdf_list = [Path(x) for x in path.iterdir() if x.name.lower().endswith('.pdf')]
        if not pdf_list and not epub_list:
            raise ValueError(0)
        if pdf_list:
            if len(pdf_list) > 1:
                log.debug('More than one PDF extracted. Not sure what to do.')
                raise ValueError(len(pdf_list))
            with pdf_list[0].open('rb') as f:
                if (sig := f.read(4)) != b'%PDF':
                    log.warning('PDF file extracted but is not a PDF.')
                    raise ValueError(sig)
            pdf_name = pdf_list[0].resolve(strict=True).parent.name
            ext = 'pdf'
        else:
            if len(epub_list) > 1:
                log.warning('More than one ePub extracted. Not sure what to do.')
                raise ValueError(len(epub_list))
            pdf_name = epub_list[0].resolve(strict=True).parent.name
            ext = 'epub'
            pdf_list = epub_list
        pdf_list[0].rename(f'../{pdf_name}.{ext}')
        for zip_file in zip_listing:
            zip_file.close()
        for x in extracted:
            x.unlink()


GOG_FILESIZE_RE = re.compile(r'filesizes="(\d+?)"')
GOG_OFFSET_RE = re.compile(r'offset=`head -n (\d+?) "\$0"')


def extract_gog(filename: StrPath, output_dir: StrPath) -> None:
    """
    Extract a Linux gog.com archive.

    Parameters
    ----------
    filename : str
        Path to the GOG archive.
    output_dir : str
        Directory to extract the files to.

    Raises
    ------
    ValueError
        If the file is not a valid GOG archive.
    """
    output_dir = Path(output_dir)
    input_path = Path(filename).resolve(strict=True)
    with input_path.open('rb') as game_bin:
        output_dir.mkdir(parents=True)
        # Read the first 10kb so we can determine the script line number
        beginning = game_bin.read(10240).decode(errors='ignore')
        offset_match = GOG_OFFSET_RE.search(beginning)
        if not offset_match:
            raise ValueError
        script_lines = int(offset_match.group(1))
        # Read the number of lines to determine the script size
        game_bin.seek(0, io.SEEK_SET)
        for _ in range(script_lines):
            game_bin.readline()
        script_size = game_bin.tell()
        log.debug('Makeself script size: %d', script_size)
        # Read the script
        game_bin.seek(0, io.SEEK_SET)
        script_bin = game_bin.read(script_size)
        with (output_dir / 'unpacker.sh').open('wb') as script_f:
            script_f.write(script_bin)
        script = script_bin.decode()
        # Filesize is for the MojoSetup archive, not the actual game data
        filesize_match = GOG_FILESIZE_RE.search(script)
        if not filesize_match:
            raise ValueError
        filesize = int(filesize_match.group(1))
        log.debug('MojoSetup archive size: %d', filesize)
        # Extract the setup archive
        game_bin.seek(script_size, io.SEEK_SET)
        with (output_dir / 'mojosetup.tar.gz').open('wb') as setup_f:
            setup_f.write(game_bin.read(filesize))
        # Extract the game data archive
        dataoffset = script_size + filesize
        game_bin.seek(dataoffset, io.SEEK_SET)
        with (output_dir / 'data.zip').open('wb') as datafile:
            shutil.copyfileobj(game_bin, datafile)


class UnRARError(Exception):
    """General ``unrar`` error."""


class UnRARExtractionTestFailed(UnRARError):
    """Raised when testing extraction fails."""


@dataclass
class RARInfo:
    """File within a RAR information."""
    attributes_str: str
    """File attributes string."""
    date: datetime
    """File date."""
    name: str
    """File name."""
    size: int
    """File size."""


class UnRAR:
    """Simple front-end to an ``unrar`` command."""
    LIST_RE = (r'^\s+'
               r'(?P<attributes>[A-Z\.]{7})\s+'
               r'(?P<size>\d+)\s+'
               r'(?P<date>(?P<year>\d{4})-'
               r'(?P<month>\d{2})-'
               r'(?P<day>\d{2})\s+'
               r'(?P<hour>\d{1,2}):'
               r'(?P<minute>\d{2}))\s+'
               r'(?P<filename>.*)')

    def __init__(self, unrar_path: StrPath = 'unrar') -> None:
        self.unrar_path = str(unrar_path)

    @contextlib.contextmanager
    def pipe(self, rar: StrPath, inner_filename: str) -> Iterator[sp.Popen[bytes]]:
        """
        Start of the pipe of the RAR's content.

        Yields
        ------
        sp.Popen[bytes]
            Handle to the ``unrar`` process.
        """
        with sp.Popen((self.unrar_path, 'p', '-y', '-inul', str(rar), inner_filename),
                      stdout=sp.PIPE,
                      close_fds=True) as p:
            yield p

    def test_extraction(self, rar: StrPath, inner_filename: str | None = None) -> None:
        """
        Test extraction.

        Raises
        ------
        UnRARExtractionTestFailed
            If the extraction test fails.
        """
        try:
            sp.run((self.unrar_path, 't', '-y', '-inul', rar,
                    *((inner_filename,) if inner_filename else ())),
                   check=True)
        except sp.CalledProcessError as e:
            raise UnRARExtractionTestFailed from e

    def list_files(self, rar: StrPath) -> Iterator[RARInfo]:
        """
        List files.

        Yields
        ------
        RARInfo
            Information about a file in the RAR archive.
        """
        for mm in (m for line in sp.run(
            (self.unrar_path, 'l', '-y',
             rar), text=True, check=True, capture_output=True).stdout.splitlines()
                   if (m := re.match(self.LIST_RE, line))):
            yield RARInfo(attributes_str=mm['attributes'],
                          date=datetime.strptime(mm['date'], '%Y-%m-%d %H:%M').replace(tzinfo=UTC),
                          name=mm['filename'],
                          size=int(mm['size']))


class SFVVerificationError(Exception):
    """Raised when SFV fails verification."""
    def __init__(self, filename: StrPath, expected_crc: int, actual_crc: int) -> None:
        super().__init__(f'{filename}: Expected {expected_crc:08X}. Actual: {actual_crc:08X}.')


def verify_sfv(sfv_file: StrPath) -> None:
    """
    Verify an SFV file.

    Raises
    ------
    SFVVerificationError
        If the CRC32 checksum does not match.
    """
    sfv_file = Path(sfv_file)
    with sfv_file.open(encoding='utf-8') as f:
        for line in (lj for lj in (li.split(';', 1)[0].split('#', 1)[0].strip() for li in f
                                   if li[0] not in {';', '#'})
                     if re.search(r'[a-z0-9]{08}$', lj, re.IGNORECASE)):
            filename, recorded_crc_s = line.rsplit(' ', 1)
            log.debug('Checking "%s".', filename)
            recorded_crc = int(recorded_crc_s, 16)
            if (crc := crc32((sfv_file.parent / filename).read_bytes())) != recorded_crc:
                raise SFVVerificationError(filename, recorded_crc, crc)


def make_sfv(sfv_file: StrPath, files: Iterable[StrPath], *, header: bool = True) -> None:
    """
    Create an SFV file.

    Parameters
    ----------
    sfv_file : str
        Path to the SFV file.
    files : Iterable[str]
        List of files to include in the SFV file.
    header : bool
        If True, include a header with the file size and date. Defaults to ``True``.
    """
    file_paths = sorted([Path(file) for file in files])
    with Path(sfv_file).open('w+', encoding='utf-8') as f:
        if header:
            f.write(f'; Generated on {datetime.now(tz=UTC).isoformat(" ")}\n')
            for file in file_paths:
                stat = file.stat()
                dt = datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat(' ')
                f.write(f'; {stat.st_size:-10d} {dt} {file.stem}\n')
        for file in file_paths:
            f.write(f'{file.name} {crc32(file.read_bytes()):08X}\n')
