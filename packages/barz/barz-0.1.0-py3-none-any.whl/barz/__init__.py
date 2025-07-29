import argparse


W = 30
B = ['', *'▏▎▍▌▋▊▉█']
C = B[-1]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('-s', '--sort', action='store_true')
    p.add_argument('-r', '--reverse', action='store_true')
    p.add_argument('file', metavar='filename', nargs='?', type=argparse.FileType(), default='-')
    args = p.parse_args()

    try:
        data: list[tuple[int, str]] = []
        d_len = 0
        n_max = 0
        n_len = 0
        for line in args.file:
            try:
                ns, rest = line.split(None, 1)
                data.append((n := int(ns, 0), rest.rstrip('\n')))
            except ValueError:
                continue
            d_len = max(d_len, len(rest))
            n_max = max(n_max, n)
            n_len = max(n_len, len(ns))

        k = n_max / W

        if args.sort:
            data = sorted(data)
        if args.reverse:
            data = data[::-1]

        for n, line in data:
            c = n / k
            bar = f'{C * int(c)}{B[round((c % 1) * 8)]}'
            print(f'{line:{d_len}}  {n:{n_len}} {bar}')
    except (BrokenPipeError, KeyboardInterrupt):
        pass


if __name__ == '__main__':
    main()
