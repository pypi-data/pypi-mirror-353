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

import sys
from typing import Any, Dict, List, Optional

from cgi import parse_header
from collections.abc import Callable
from lockss.pybasic.cliutil import BaseCli, StringCommand, exactly_one, one_or_more, COPYRIGHT_DESCRIPTION, LICENSE_DESCRIPTION, VERSION_DESCRIPTION
from lockss.pybasic.errorutil import InternalError
from lockss.pybasic.fileutil import file_lines, path
from pathlib import Path
from pydantic.v1 import BaseModel, Field, root_validator, validator
from pydantic.v1.types import FilePath

from . import __copyright__, __license__, __version__
from .warcutil import browse_responses, open_warc, WarcRecord


_columns: Dict[str, Callable[[Path, WarcRecord], Any]] = {
    'url': lambda f, r: r.get_url(), # is intentionally first
    'content_type': lambda f, r: r.get_http_headers().get('Content-Type'),
    'http_code': lambda f, r: r.get_http_code(),
    'http_date': lambda f, r: r.get_http_headers().get('Date'),
    'http_protocol': lambda f, r: r.get_http_protocol(),
    'http_reason': lambda f, r: r.get_http_reason(),
    'http_status': lambda f, r: r.get_http_status(),
    'media_type': lambda f, r: parse_header(r.get_http_headers().get('Content-Type', ''))[0],
    'warc_date': lambda f, r: r.get_date(),
    'warc_file': lambda f, r: f
}


class WarcsOptions(BaseModel):
    warc: Optional[List[FilePath]] = Field([], aliases=['-w'], description='[WARCs] add one or more WARC files to the list of WARC files to process')
    warcs: Optional[List[FilePath]] = Field([], aliases=['-W'], description='[WARCs] add the WARC files listed in one or more files to the list of WARC files to process')

    @validator('warc', 'warcs', pre=True, each_item=True)
    def _expand_each_warcs_path(cls, v: Path):
        return path(v)

    def get_warcs(self):
        ret = [*self.warc[:], *[file_lines(file_path) for file_path in self.warcs]]
        if len(ret) == 0:
            raise RuntimeError('empty list of WARC files')
        return ret


class ExtractOptions(BaseModel):
    target_url: str = Field(aliases=['-T'], description='[target] target URL')
    http_headers: Optional[bool] = Field(False, aliases=['-H', '--hh'], description='[action] extract HTTP headers for target URL')
    http_payload: Optional[bool] = Field(False, aliases=['-P', '--hp'], description='[action] extract HTTP payload for target URL')
    warc_headers: Optional[bool] = Field(False, aliases=['-A', '--wh'], description='[action] extract WARC headers for target URL')

    @root_validator
    def _exactly_one_action(cls, values):
        return exactly_one(values, 'http_headers', 'http_payload', 'warc_headers')


class ReportOptions(BaseModel):
    content_type: Optional[bool] = Field(False, aliases=['-c'], description='[column] include HTTP Content-Type (e.g. text/xml; charset=UTF-8)')
    http_code: Optional[bool] = Field(False, aliases=['-n'], description='[column] include HTTP response code (e.g. 404)')
    http_date: Optional[bool] = Field(False, aliases=['-d'], description='[column] include HTTP Date')
    http_protocol: Optional[bool] = Field(False, aliases=['-p'], description='[column] include HTTP protocol (e.g. HTTP/1.1)')
    http_reason: Optional[bool] = Field(False, aliases=['-r'], description='[column] include HTTP reason (e.g. Not Found)')
    http_status: Optional[bool] = Field(False, aliases=['-s'], description='[column] include HTTP status (e.g. HTTP/1.1 404 Not Found)')
    media_type: Optional[bool] = Field(False, aliases=['-m'], description='[column] include media type of HTTP Content-Type (e.g. text/xml)')
    url: Optional[bool] = Field(False, aliases=['-u'], description='[column] include URL of WARC record')
    warc_date: Optional[bool] = Field(False, aliases=['-D'], description='[column] include date of WARC record')
    warc_file: Optional[bool] = Field(False, aliases=['-F'], description='[column] include name of WARC file')

    @root_validator
    def _one_or_more_columns(cls, values):
        return one_or_more(values, *ReportOptions.__fields__.keys())


class ExtractCommand(ExtractOptions, WarcsOptions): pass
class ReportCommand(ReportOptions, WarcsOptions): pass


class WarcReadCommand(BaseModel):
    copyright: Optional[StringCommand.type(__copyright__)] = Field(description=COPYRIGHT_DESCRIPTION)
    extract: Optional[ExtractCommand] = Field(description='extract parts of response records')
    license: Optional[StringCommand.type(__license__)] = Field(description=LICENSE_DESCRIPTION)
    report: Optional[ReportCommand] = Field(description='output tab-separated report over response records')
    version: Optional[StringCommand.type(__version__)] = Field(description=VERSION_DESCRIPTION)


class WarcReadCli(BaseCli[WarcReadCommand]):

    def __init__(self):
        super().__init__(model=WarcReadCommand,
                         prog='warcread',
                         description='Tool for WARC file reporting')

    def _copyright(self, copyright_model: StringCommand) -> None:
        self._do_string_command(copyright_model)

    def _do_string_command(self, string_command: StringCommand) -> None:
        string_command.action()

    def _extract(self):
        eargs = self.args.extract
        url = eargs.target_url
        for warc_path in eargs.get_warcs():
            warc = open_warc(warc_path)
            for record in browse_responses(warc):
                if record.get_url() == url:
                    if eargs.http_headers:
                        for k, v in record.get_http_headers().items():
                            if not k.startswith('$'):
                                print(f'{k}: {v}')
                    elif eargs.http_payload:
                        for line in record.get_http_payload():
                            print(line, end='')
                    elif eargs.warc_headers:
                        for k, v in record.get_warc_headers().items():
                            print(f'{k}: {v}')
                    else:
                        raise InternalError()
                    return
        else:
            sys.exit(f'Target URL not found: {url}')

    def _license(self, license_model: StringCommand) -> None:
        self._do_string_command(license_model)

    def _report(self):
        rargs = self.args.report
        for warc_path in rargs.get_warcs():
            warc = open_warc(warc_path)
            for record in browse_responses(warc):
                print('\t'.join([str(lam(path, record)) for key, lam in _columns.items() if getattr(rargs, key)]))

    def _version(self, version_model: StringCommand) -> None:
        self._do_string_command(version_model)


def main():
    WarcReadCli().run()


if __name__ == '__main__':
    main()
