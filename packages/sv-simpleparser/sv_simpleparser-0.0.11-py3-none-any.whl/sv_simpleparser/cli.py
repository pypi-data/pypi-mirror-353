# MIT License
#
# Copyright (c) 2025 ericsmacedo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
def gen_sv_instance(file_path):
    """Parses an SystemVerilog file and returns a instance of the module"""
    from ._gen_templates import gen_instance
    from ._sv_parser import parse_sv

    mod_lst = parse_sv(file_path)

    for mod_obj in mod_lst:
        instance = gen_instance(mod_obj)
        print(instance)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
def gen_io_table(file_path):
    """Generates an I/O table from an SV file"""
    from ._gen_templates import gen_markdown_table
    from ._sv_parser import parse_sv

    mod_lst = parse_sv(file_path)

    for mod_obj in mod_lst:
        table = gen_markdown_table(mod_obj)
        print(table)


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, readable=True))
def print_tokens(file_path):
    """Print tokens for debug"""

    from ._sv_parser import parse_sv

    parse_sv(file_path)
