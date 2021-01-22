#!/usr/bin/python

import random, sys, argparse, string

def parseNumList(string):
    start = int(string[0])
    end = int(string[2])
    return list(range(start, end+1))

def main():
    version_msg = "%prog 2.0"
    usage_msg = """%prog [OPTION]... FILE

shuffles lines and outputs either all or a selected number of lines."""
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument("-", action="store_true", dest="-", help="Read in from standard input")
    parser.add_argument("-n", "--head-count", action="store", dest="numlines", help="output NUMLINES lines (default 1)")
    parser.add_argument('-e','--echo', nargs='+', dest="echo",
                        help='treat each ARG as an input line')
    parser.add_argument("-i", "--input-range", action="store", dest="range", type=parseNumList,
                        help="treat each number LO through HI as an input line")
    parser.add_argument("-r", "--repeat", action="store_true", dest="repeat", default=False,
                        help="output lines can be repeated")

    options = parser.parse_args()
    args = sys.argv[1:]


    lines = []

    if options.infile.name != '<stdin>':
        if options.echo or options.range:
            raise RuntimeError('shuf: cannot combine file input')
        try:
            lines = open(options.infile.name, 'r').read().split('\n')
        except IOError as exc:
            raise RuntimeError('Failed to open database') from exc
    elif options.range:
        if options.echo:
            raise RuntimeError('shuf: cannot combine -e and -i options')
        lines = options.range.copy()
    elif options.echo:
        lines = options.echo.copy()
    else:
        f = sys.stdin.readlines().copy()
        lines = [line.strip('\n') for line in f]

    if options.numlines:
        try:
            numlines = int(options.numlines)
        except:
            parser.error("invalid NUMLINES: {0}".
                         format(options.numlines))
        if numlines < 0:
            parser.error("negative count: {0}".
                         format(numlines))
    if options.repeat:
        if options.numlines:
            for index in range(numlines):
                print(random.choice(lines))
        else:
            while lines:
                print(random.choice(lines))
    else:
        if options.numlines:
            if numlines > len(lines):
                numlines = len(lines)
        else:
            numlines = len(lines)
        output = random.sample(lines, k=numlines)
        for index in range(numlines):
            print(output[index])

if __name__ == "__main__":
    main()
