# Contributing to **pypekit**

## Setup

1. Fork & clone this repo.
2. Install project + dev tools:
   ```bash
   pip install .[dev,docs]
   ```
3. Check the installation:
   ```bash
   hatch run check
   ```

## Commits & PRs

* Follow conventional commits (`feat: …`, `fix: …`, `docs: …`).
* Run `hatch run fmt` to auto format your code.
* Run `hatch run docs` to preview the documentation on `localhost:8000`.
* Run `hatch run check` to check formating, run tests, and build the documentation.
* Open a pull request.
