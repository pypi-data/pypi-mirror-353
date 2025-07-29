# pycamp

a command-line tool to fetch a random bandcamp album from a chosen genre — instantly.

## features

- open random bandcamp albums by tag/genre
- two modes:
  - `quick`: quick, no album details, just opens it
  - `full`: fetch album details (title, artist, date, tags) before prompting to open
- works with any genre tag on bandcamp
- supports short flags for fast access (`-q`, `-f`)

## installation

```bash
pip install pycamp-cli
```

## usage

```bash
pycamp <genre> [ --quick | -q | --full | -f ]
```

### Examples

```bash
pycamp hardcore
pycamp ambient --full
pycamp blackened crust -q
```

if no flag is provided, `--quick` is the default.

## flags

| flag         | mode description                        |
|--------------|------------------------------------------|
| `--quick` or `-q` | quick mode — skips detail fetch, just opens    |
| `--full` or `-f`  | full mode — shows album info before prompting  |

## notes

- uses playwright under the hood. on first run, you may need to install browser dependencies:

```bash
playwright install
```

- make sure `node` and a recent python (3.7+) are installed.

## tip

use specific genres like:

- `trip hop`
- `blackened crust`
- `powerviolence`
- `spiritual jazz`
- `grindcore`

they map directly to bandcamp tag pages.

## license

MIT © jasper binetti-makin