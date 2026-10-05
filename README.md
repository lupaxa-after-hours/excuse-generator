<p align="center">
  <a href="https://github.com/lupaxa-after-hours">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/after-hours/readme-logo.png" alt="After Hours" />
  </a>
</p>

<h1 align="center">Excuse Generator</h1>

Generate a random excuse from a category and an absurdity level. The same
package is a small Python library and a pipe-friendly command.

The PyPI name is `lupaxa-excuse-generator`. The import path is
`lupaxa.excuse_generator`. The console script is `excuse-generator`.
`lupaxa` is a namespace package — there is no `lupaxa/__init__.py`.

Public names: `get_excuse`, `get_excuses`, `get_blame`, `Category`, `Level`,
`ExcuseError`, `InvalidCategoryError`, `InvalidLevelError`,
`ExcuseDataError`, `__version__`, `get_version()`.

Friday excuses are a normal category. Ask for them with `--category friday`.
The tool does not look at the date.

## Install

```bash
pip install lupaxa-excuse-generator
```

Requires Python 3.10+. The standard library is enough.

## CLI

```bash
excuse-generator
excuse-generator --category coding --level questionable
excuse-generator --count 5
excuse-generator --blame
excuse-generator --seed 42
excuse-generator --version
```

One excuse is printed per line. There is no banner.

| Flag                  | Meaning                                          |
| --------------------- | ------------------------------------------------ |
| `-c`, `--category`    | Limit excuses to one category                    |
| `-l`, `--level`       | Limit excuses to one absurdity level             |
| `-n`, `--count`       | Print this many excuses (1 to 100)               |
| `--blame`             | Print one thing to blame                         |
| `--categories`        | List categories and exit                         |
| `--levels`            | List absurdity levels and exit                   |
| `--seed`              | Seed generation for a repeatable result          |
| `--version`           | Print `excuse-generator x.y.z` and exit `0`      |
| `--help`              | Show argparse help                               |

`--blame` cannot be combined with `--category`, `--level`, or `--count`.
`--categories` and `--levels` cannot be combined with each other or with
generation options.

| Result                         | Stdout                     | Exit |
| ------------------------------ | -------------------------- | ---- |
| Success                        | One excuse per line        | `0`  |
| `--version`                    | `excuse-generator x.y.z`   | `0`  |
| Invalid arguments              | error on stderr            | `2`  |
| Broken packaged data           | error on stderr            | `1`  |

```bash
python -m lupaxa.excuse_generator --category friday
```

## Library

```python
from lupaxa.excuse_generator import get_blame, get_excuse, get_excuses

get_excuse(category="coding", level="absurd")
get_excuses(5, category="meeting")
get_blame()
```

Pass `rng=random.Random(seed)` when a test needs the same result twice.
That object is the only random state the library uses.

Excuses live in `data/excuses.json`. Blame lives in `data/blame.json`.

| Call                                      | Return                          |
| ----------------------------------------- | ------------------------------- |
| `get_excuse()`                            | one excuse from any pool        |
| `get_excuse(category="coding")`           | one coding excuse               |
| `get_excuses(count, category, level)`     | `count` excuses                 |
| `get_blame()`                             | one blame entry                 |

| Situation                          | Result                  |
| ---------------------------------- | ----------------------- |
| Unknown category                   | `InvalidCategoryError`  |
| Unknown level                      | `InvalidLevelError`     |
| `count` below 1                    | `ValueError`            |
| Packaged data is missing or wrong  | `ExcuseDataError`       |

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
