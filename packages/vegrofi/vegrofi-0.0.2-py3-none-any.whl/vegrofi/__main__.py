# Copyright (c) 2025 Andrey Rybakov

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
from argparse import ArgumentParser

from termcolor import colored, cprint

from vegrofi import __release_date__, __version__


def decorate(line):
    line = line.split("\n")[0]

    return f'\n    "{line}".\n'


def check_separator(lines, i, error_messages):
    line = lines[i].split()

    if len(line) != 1 or not set(line[0].split("=")) == {""}:
        error_messages.append(
            f"Line {i+1}: Expected section separator, i.e. line that consist of "
            f'approximately 80 "=" symbols, got {decorate(lines[i])}'
        )


def check_subseparator(lines, i, error_messages):
    line = lines[i].split()

    if len(line) != 1 or not set(line[0].split("-")) == {""}:
        error_messages.append(
            f"Line {i+1}: Expected subsection separator, i.e. line that consist of "
            f'approximately 40 "-" symbols, got {decorate(lines[i])}'
        )


def check_convention(lines, i, error_messages):
    if i > 0:
        check_separator(lines=lines, i=i - 1, error_messages=error_messages)

    if len(lines) <= i + 5:
        error_messages.append(
            f"Expected  five lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i

    i += 1
    line = lines[i].split()
    if (
        len(line) < 3
        or line[0].lower() != "double"
        or line[1].lower() != "counting"
        or line[2].lower() != "true"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Double counting true" (with at least one space '
            f"between each pair of words), got {decorate(lines[i])}"
        )

    i += 1
    line = lines[i].split()
    if (
        len(line) < 3
        or line[0].lower() != "normalized"
        or line[1].lower() != "spins"
        or line[2].lower() != "true"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Normalized spins true" (with at least one space '
            f"between each pair of words), got {decorate(lines[i])}"
        )

    i += 1
    line = lines[i].split()
    if (
        len(line) < 3
        or line[0].lower() != "intra-atomic"
        or line[1].lower() != "factor"
        or line[2].lower() != "+1"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Intra-atomic factor +1" (with at least one space '
            f"between each pair of words), got {decorate(lines[i])}"
        )

    i += 1
    line = lines[i].split()
    if (
        len(line) < 3
        or line[0].lower() != "exchange"
        or line[1].lower() != "factor"
        or line[2].lower() != "+0.5"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Exchange factor +0.5" (with at least one space '
            f"between each pair of words), got {decorate(lines[i])}"
        )

    i += 1
    check_separator(lines=lines, i=i, error_messages=error_messages)
    return i


def check_cell(lines, i, error_messages):
    if i > 0:
        check_separator(lines=lines, i=i - 1, error_messages=error_messages)

    if len(lines) <= i + 4:
        error_messages.append(
            f"Expected four lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i

    for _ in range(3):
        i += 1
        line = lines[i].split()
        if len(line) < 3:
            error_messages.append(
                f"Line {i+1}: Expected three numbers separated by at least one space "
                f"symbol, got {decorate(lines[i])}"
            )

        try:
            a = list(map(float, line[:3]))
        except:
            error_messages.append(
                f"Line {i+1}: Expected three numbers convertable to floats, got {decorate(lines[i])}"
            )

    i += 1
    check_separator(lines=lines, i=i, error_messages=error_messages)
    return i


def check_magnetic_sites(lines, i, error_messages):
    if i > 0:
        check_separator(lines=lines, i=i - 1, error_messages=error_messages)

    i_zero = i

    if len(lines) <= i + 3:
        error_messages.append(
            f"Expected at least three lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i, None

    i += 1
    line = lines[i].split()
    M = None
    if (
        len(line) < 4
        or line[0].lower() != "number"
        or line[1].lower() != "of"
        or line[2].lower() != "sites"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Number of sites" followed by a single integer '
            f"(with at least one space between each pair of words), got {decorate(lines[i])}"
        )
    else:
        try:
            M = int(line[3])
        except:
            error_messages.append(
                f'Line {i+1}: Expected "Number of sites" followed by a single integer '
                f"(with at least one space between each pair of words), got {decorate(lines[i])}"
            )

    i += 1
    line = lines[i].split()
    if (
        len(line) < 11
        or line[0].lower() != "name"
        or line[1].lower() != "x"
        or line[2].lower() != "(ang)"
        or line[3].lower() != "y"
        or line[4].lower() != "(ang)"
        or line[5].lower() != "z"
        or line[6].lower() != "(ang)"
        or line[7].lower() != "s"
        or line[8].lower() != "sx"
        or line[9].lower() != "sy"
        or line[10].lower() != "sz"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Name x (Ang) y (Ang) z (Ang) s sx sy sz" '
            f"(with at least one space between each pair of words), got {decorate(lines[i])}"
        )

    if M is None:
        return i, None
    elif len(lines) <= i + M + 1:
        error_messages.append(
            f"Expected at least {M+1} lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i, None

    names = []
    for _ in range(M):
        i += 1
        line = lines[i].split()
        if len(line) < 8:
            error_messages.append(
                f"Line {i+1}: Expected one string and seven numbers, separated by at "
                f"least one space symbol, got {decorate(lines[i])}"
            )
        else:
            names.append(line[0])
            try:
                for j in range(1, 8):
                    float(line[j])
            except:
                error_messages.append(
                    f"Line {i+1}: Expected one string and seven numbers, separated by at "
                    f"least one space symbol, got {decorate(lines[i])}"
                )
    i += 1
    check_separator(lines=lines, i=i, error_messages=error_messages)

    if len(names) != M:
        return i, None

    if len(names) != len(set(names)):
        error_messages.append(
            f"Lines {i_zero+1}-{i+1}: Names of the magnetic sites are not unique."
        )
    return i, names


def check_intra_atomic(lines, i, error_messages, names):
    if i > 0:
        check_separator(lines=lines, i=i - 1, error_messages=error_messages)

    if names is None:
        error_messages.append(
            f"Cannot verify Inra-atomic section due to the problems with the Magnetic "
            "sites section."
        )
        return i
    if len(lines) <= i + len(names) * 6 + 1:
        error_messages.append(
            f"Expected at least {len(names) * 6+1} lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i

    i += 1
    check_subseparator(lines=lines, i=i, error_messages=error_messages)

    for _ in range(len(names)):
        i += 1
        line = lines[i].split()
        if len(line) == 0:
            error_messages.append(
                f"Line {i+1}: Expectted a name of the magnetic site, got nothing."
            )
        else:
            if line[0] not in names:
                error_messages.append(
                    f'Line {i+1}: Name of the atom "{line[0]}" is not present in '
                    f'the "Magnetic sites" section'
                )

        i += 1
        line = lines[i].split()
        if len(line) == 0 or line[0].lower() != "matrix":
            error_messages.append(
                f'Line {i+1}: Expected a keyword "Matrix", got {decorate(lines[i])}'
            )

        for _ in range(3):
            i += 1
            line = lines[i].split()
            if len(line) < 3:
                error_messages.append(
                    f"Line {i+1}: Expected three numbers separated by at least one space "
                    f"symbol, got {decorate(lines[i])}"
                )

            try:
                a = list(map(float, line[:3]))
            except:
                error_messages.append(
                    f"Line {i+1}: Expected three numbers convertable to floats, got {decorate(lines[i])}"
                )

        i += 1
        check_subseparator(lines=lines, i=i, error_messages=error_messages)

    i += 1
    check_separator(lines=lines, i=i, error_messages=error_messages)
    return i


def check_exchange(lines, i, error_messages, names):
    if i > 0:
        check_separator(lines=lines, i=i - 1, error_messages=error_messages)

    if names is None:
        error_messages.append(
            f"Cannot verify Exchange section due to the problems with the Magnetic "
            "sites section."
        )
        return i

    if len(lines) <= i + 4:
        error_messages.append(
            f"Expected at least four lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i

    i += 1
    line = lines[i].split()
    N = None
    if (
        len(line) < 4
        or line[0].lower() != "number"
        or line[1].lower() != "of"
        or line[2].lower() != "pairs"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Number of pairs" followed by a single integer '
            f"(with at least one space between each pair of words), got {decorate(lines[i])}"
        )
    else:
        try:
            N = int(line[3])
        except:
            error_messages.append(
                f'Line {i+1}: Expected "Number of pairs" followed by a single integer '
                f"(with at least one space between each pair of words), got {decorate(lines[i])}"
            )

    i += 1
    check_subseparator(lines=lines, i=i, error_messages=error_messages)

    i += 1
    line = lines[i].split()
    if (
        len(line) < 7
        or line[0].lower() != "name1"
        or line[1].lower() != "name2"
        or line[2].lower() != "i"
        or line[3].lower() != "j"
        or line[4].lower() != "k"
        or line[5].lower() != "d"
        or line[6].lower() != "(ang)"
    ):
        error_messages.append(
            f'Line {i+1}: Expected "Name1 Name2 i j k d  (Ang)" '
            f"(with at least one space between each pair of words), got {decorate(lines[i])}"
        )

    i += 1
    check_subseparator(lines=lines, i=i, error_messages=error_messages)

    if N is None:
        return i
    elif len(lines) <= i + N * 6 + 1:
        error_messages.append(
            f"Expected at least {N * 6 + 1} lines after the line {i+1}, "
            f"got {len(lines) - i - 1} before the end of file."
        )
        return i

    for _ in range(N):
        i += 1
        line = lines[i].split()
        if len(line) < 6:
            error_messages.append(
                f"Line {i+1}: Expectted two names of the magnetic site, followed by "
                f"three integers and one float, got {decorate(lines[i])}"
            )
        else:
            if line[0] not in names:
                error_messages.append(
                    f'Line {i+1}: Name of the first atom "{line[0]}" is not present in '
                    f'the "Magnetic sites" section'
                )
            if line[1] not in names:
                error_messages.append(
                    f'Line {i+1}: Name of the second atom "{line[1]}" is not present in '
                    f'the "Magnetic sites" section'
                )

            try:
                for j in range(3):
                    int(line[2 + j])
                float(line[5])
            except:
                error_messages.append(
                    f"Line {i+1}: Expectted two names of the magnetic site, followed by "
                    f"three integers and one float, got {decorate(lines[i])}"
                )

        i += 1
        line = lines[i].split()
        if len(line) == 0 or line[0].lower() != "matrix":
            error_messages.append(
                f'Line {i+1}: Expected a keyword "Matrix", got {decorate(lines[i])}'
            )

        for _ in range(3):
            i += 1
            line = lines[i].split()
            if len(line) < 3:
                error_messages.append(
                    f"Line {i+1}: Expected three numbers separated by at least one space "
                    f"symbol, got {decorate(lines[i])}"
                )

            try:
                a = list(map(float, line[:3]))
            except:
                error_messages.append(
                    f"Line {i+1}: Expected three numbers convertable to floats, got {decorate(lines[i])}"
                )

        i += 1
        check_subseparator(lines=lines, i=i, error_messages=error_messages)

    i += 1
    check_separator(lines=lines, i=i, error_messages=error_messages)
    return i


def check_file(filename):
    error_messages = []
    found_convention = False
    found_cell = False
    found_sites = False
    found_intra_atomic = False
    found_exchange = False

    with open(filename, "r") as f:
        lines = f.readlines()

    i = 0
    check_separator(lines=lines, i=0, error_messages=error_messages)
    names = None
    while i < len(lines):
        if "Hamiltonian convention" in lines[i]:
            found_convention = True
            i = check_convention(i=i, lines=lines, error_messages=error_messages)

        if "Cell (Ang)" in lines[i]:
            found_cell = True
            i = check_cell(i=i, lines=lines, error_messages=error_messages)

        if "Magnetic sites" in lines[i]:
            if not found_cell:
                error_messages.append(
                    "Expected to find Cell section before Magnetic sites section."
                )
            found_sites = True
            i, names = check_magnetic_sites(
                i=i, lines=lines, error_messages=error_messages
            )
        if "Intra-atomic anisotropy tensor (meV)" in lines[i]:
            if not found_convention or not found_cell or not found_sites:
                error_messages.append(
                    "Expected to find Cell, Convention and Magnetic sites sections "
                    "before Intra-atomic anisotropy section."
                )
            found_intra_atomic = True
            i = check_intra_atomic(
                i=i, lines=lines, error_messages=error_messages, names=names
            )
        if "Exchange tensor (meV)" in lines[i]:
            if not found_convention or not found_cell or not found_sites:
                error_messages.append(
                    "Expected to find Cell, Convention and Magnetic sites sections "
                    "before Exchange section."
                )
            found_exchange = True
            i = check_exchange(
                i=i, lines=lines, error_messages=error_messages, names=names
            )

        i += 1

    if not found_convention:
        error_messages.append("Section with the convention is not found.")
    if not found_cell:
        error_messages.append("Section with the unit cell is not found.")
    if not found_sites:
        error_messages.append("Section with the magnetic sites is not found.")
    if not found_intra_atomic:
        error_messages.append(
            "Section with the intra-atomic anisotropy parameters is not found."
        )
    if not found_exchange:
        error_messages.append("Section with the exchange parameters is not found.")

    return error_messages


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "filenames",
        metavar="filename1 filename2 ...",
        type=str,
        nargs="*",
        help="Files with spin Hamiltonian produced by GROGU.",
    )

    logo = [
        "  ██╗   ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗██╗",
        "  ██║   ██║██╔════╝██╔════╝ ██╔══██╗██╔═══██╗██╔════╝██║",
        "  ██║   ██║█████╗  ██║  ███╗██████╔╝██║   ██║█████╗  ██║",
        "  ╚██╗ ██╔╝██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  ██║",
        "   ╚████╔╝ ███████╗╚██████╔╝██║  ██║╚██████╔╝██║     ██║",
        "    ╚═══╝  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝",
        " " * 46 + "▄   ▄     ",
        f"{f'Version: {__version__}':^46}" + "█▀█▀█     ",
        f"{f'Relese date: {__release_date__}':^46}" + "█▄█▄█     ",
        f"{'License: MIT license':^46}" + " ███   ▄▄ ",
        f"{'Copyright (C): 2025 Andrey Rybakov':^46}" + " ████ █  █",
        " " * 46 + " ████    █",
        " " * 46 + " ▀▀▀▀▀▀▀▀ ",
    ]
    print("\n".join(logo))

    filenames = parser.parse_args().filenames

    ok_files = []
    not_ok_files = []
    for filename in filenames:
        if not os.path.isfile(filename):
            cprint(f"File {os.path.abspath(filename)} not found.", color="red")
            sys.exit(1)

        print(f"\n{' Start check ':=^80}")
        print(f'Checking a file "{os.path.abspath(filename)}"')

        error_messages = check_file(filename=filename)

        if len(error_messages) == 0:
            ok_files.append(filename)
            cprint(f"{' It is a valid GROGU file ':=^80}\n", color="green")
        else:
            not_ok_files.append(filename)
            cprint("\n".join(error_messages), color="red")
            cprint(f"{' It is NOT a valid GROGU file ':=^80}\n", color="red")

    if len(ok_files) == 1:
        cprint(f"File\n    " + "\n    ".join(ok_files) + "\nis OK", color="green")
    elif len(ok_files) > 1:
        cprint(f"Files\n    " + "\n    ".join(ok_files) + "\nare OK", color="green")
    if len(not_ok_files) == 1:
        cprint(f"File\n    " + "\n    ".join(not_ok_files) + "\nis NOT OK", color="red")
        sys.exit(1)
    elif len(not_ok_files) > 1:
        cprint(
            f"Files\n    " + "\n    ".join(not_ok_files) + "\nare NOT OK", color="red"
        )


if __name__ == "__main__":
    main()
