# barz

## Installation
```sh
uv tool install barz
```
```sh
pipx install barz
```

## Usage
```console
$ barz --help
usage: barz [-h] [-s] [-r] [filename]

positional arguments:
  filename

options:
  -h, --help     show this help message and exit
  -s, --sort
  -r, --reverse

$ python3 -c "print(*['asdf']*100, *['qwer']*15, *['zxcv']*34, sep='\n')" | uniq -c | barz
asdf   100 ██████████████████████████████
qwer    15 ████▌
zxcv    34 ██████████▎

$ python3 -c "print(*['asdf']*100, *['qwer']*15, *['zxcv']*34, sep='\n')" | uniq -c | barz -r
zxcv    34 ██████████▎
qwer    15 ████▌
asdf   100 ██████████████████████████████

$ python3 -c "print(*['asdf']*100, *['qwer']*15, *['zxcv']*34, sep='\n')" | uniq -c | barz -s
qwer    15 ████▌
zxcv    34 ██████████▎
asdf   100 ██████████████████████████████

$ python3 -c "print(*['asdf']*100, *['qwer']*15, *['zxcv']*34, sep='\n')" | uniq -c | barz -sr
asdf   100 ██████████████████████████████
zxcv    34 ██████████▎
qwer    15 ████▌
```
