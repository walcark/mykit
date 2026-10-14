# mykit — specification

mykit makes scientific projects easier to run, develop and read. It is aimed at projects built on
remote-sensing data: many files laid out by tile, date or band, rasters and cubes, and compute on
a SLURM cluster. Nothing in it is specific to one project.

This file is the reference the tutorials build towards. It changes when a tutorial shows that a
decision was wrong: record the change and its reason in `PROGRESS.md`.

## 1. Shape

- **One importable library.** All logic lives in Python functions you can call from a script, a notebook or a test.
- **A thin CLI on top.** Each command parses arguments, calls one library function and prints the result. No logic lives only in the CLI.
- **Not a wrapper.** Functions return standard objects: `DataFrame`, `GeoDataFrame`, `xr.Dataset`, `Path`. Only three classes are mykit's own: `Layout`, `Run`, `Job`.
- **Lazy domains.** `import mykit` loads nothing heavy; a domain is imported on first access.
- **Extras** keep the core light: `data` (pandas, xarray, zarr, pyarrow), `geo` (geopandas, rioxarray), `viz` (matplotlib, scienceplots), `big` (dask, distributed, dask-jobqueue).

## 2. Principles

1. Standard data in, standard data out. No class wraps a DataFrame or a Dataset.
2. Functions first; a class only for what has an identity (`Layout`, `Run`, `Job`).
3. No global state, no magic. A script receives its run as a parameter; its inputs are declared.
4. Nothing ambiguous passes silently: an ambiguous file name, an unknown filter, a missing root, an unknown configuration key each raise an error that says what to do.
5. Four storage places, four meanings: `data` is read-only, `runs` are written once, `cache` can be recomputed, `results` is the versioned selection.
6. Strict layers, checked by a test: analysis never imports the workflow domains, and mykit never imports a pack.
7. A budget: at most five public names per domain, at most 300 lines per module.
8. The rule of two: code moves into mykit when a second project needs it, with its tests.

## 3. Domains

### Workflow

| Domain    | Role                                                                              | Public names                                 |
|-----------|-----------------------------------------------------------------------------------|----------------------------------------------|
| `log`     | Readable console logs, JSON-lines files, a fixed event vocabulary                 | `setup`, `event`, `timed`, `context`, `read` |
| `project` | Project root, machine and project configuration, named paths and layouts, secrets | `root`, `path`, `layout`, `secret`           |
| `files`   | Find files by name, read them (also as a cube), write once, cache                 | `Layout`, `load`, `save`, `cached`           |
| `runs`    | A traced script: parameters, declared inputs, groups, manifest, search            | `script`, `find`, `get`, class `Run`         |
| `cluster` | Run locally or on SLURM without writing sbatch files                              | `submit`, class `Job`                        |

### Analysis

| Domain  | Role                                                                | Public names                                             |
|---------|---------------------------------------------------------------------|----------------------------------------------------------|
| `stats` | Compare an estimate with a reference                                | `compare`, `binned`                                      |
| `viz`   | Style, plumbing, colours tied to meaning, recipes that take an `ax` | `style`, `figure`, `colorbar`, `save`, `colors`, recipes |
| `geo`   | What geopandas and rioxarray do not do alone                        | `points`, `locate`, `sample`, `to_qgis`                  |
| `dates` | Split and group periods; a period is always a `slice`               | `split`, `groups`                                        |

Scientific domains (`optics`, `montecarlo`, `atmo`, …) grow by the rule of two.

## 4. Key contracts

**Logs.**

- A library never configures logging on import; `setup` is called by entry points only.
- Console output is human-readable, with colours only when the stream is a terminal. Files hold one JSON object per line, never colours.
- Event names are `<subject>.<phase>`:
  - subjects: `run`, `module`, `step`, `job`, `cache`, `io`;
  - phases: `start`, `done`, `failed`, `cached`, `skipped`;
  - `done` requires `duration_s`, `failed` requires `duration_s` and `error`, `skipped` requires `reason`.
- Messages from other libraries are kept, as the event `message`.

**Configuration.**

- Two TOML files: `~/.config/mykit/config.toml` (the machine: real paths, cluster, `include`s) and `mykit.toml` (the project: names, never machine paths). The project wins; tables merge, lists replace.
- A project refers to a machine path as `@name`. Unknown keys raise.
- A job reads a frozen copy of the resolved configuration.
- Scientific parameters never go in configuration files: they belong to scripts.

**Layout.**

- A path template with typed fields (`{date:%Y%m%d}`, `{n:03d}`, `{band}`), read both ways: `find` returns a typed DataFrame, `parse` returns the fields of a path, `path` builds a path.
- One filter grammar, shared with `runs.find` and the CLI:
  - a value means equality at its own precision (`"2023-01"` is the whole month);
  - a list means any of;
  - a slice is a closed range;
  - a tuple matches a sequence-valued run parameter, and is refused by a Layout.
- A path that reads two ways raises, showing both readings.

**Runs.**

- `@runs.script` turns a function's signature into a CLI. Every launch is a group of runs, under `runs/<name>/<stamp>/<task>/` with a `run.json` manifest: parameters, inputs, git commit and diff, host, SLURM ids, status, records, outputs.
- Inputs are declared (`inputs=["samples"]`), resolved to a group when launched, shown, and written into the manifest and into the generated job script.

**Cluster.**

- `submit` takes a `runs.script` or any command, with `over` for arrays and `after` / `after_any` for dependencies.
- The generated sbatch script is readable and saved, and `dry=True` shows it without submitting. A `local` profile runs the same jobs as subprocesses.

## 5. Around the library

- **CLI** `mk`: `new`, `submit`, `jobs`, `runs`, `status`, `rerun`, `gc`, `config`, `logs`.
- **Project template**, a separate copier repository. It holds `scripts/`, `src/`, `notes/`, `tests/` (with a `conftest.py` that isolates runs), marimo notebooks, and a correct `.gitignore`.
- **Packs**, separate packages for a site, a mission or a product format. They depend on mykit, never the other way round. They plug in through configuration (a TOML file the machine configuration includes) and through mykit's public API.

## 6. Goals coverage

| Goal                                          | Where                                                  |
|-----------------------------------------------|--------------------------------------------------------|
| Know where data is, on any machine            | `project`, configuration with `@name`                  |
| Find files easily                             | `files.Layout`                                         |
| Save easily, never overwrite, know the origin | `run.save`, manifests                                  |
| Search past results                           | `runs.find`, `mk status`, `mk runs`                    |
| Avoid recomputing                             | `files.cached`, content-keyed cache                    |
| xarray, geopandas, dask, QGIS processing      | standard objects, `files.load` to cubes, `geo`, extras |
| Launch on the cluster without writing SLURM   | `cluster.submit`, `mk submit`                          |
| Statistics, learning, visualisation           | `stats`, `viz`, run records for model selection        |
| Quick scaffolding of research scripts         | the template, `mk new`                                 |
| Timing and debugging from logs                | `log` vocabulary, `log.read`, `mk logs`                |
| Evolvable over time                           | lazy domains, packs, schema versions, the rule of two  |

## 7. Tutorials

| TP | Topic                                           |
|----|-------------------------------------------------|
| 0  | Package skeleton                                |
| 1  | `log`                                           |
| 2  | `project` and configuration                     |
| 3  | `files.save` and `files.load`                   |
| 4  | `Layout`, part 1: templates, `parse`, `path`    |
| 5  | `Layout`, part 2: `find` and the filter grammar |
| 6  | Tables to cubes, and `files.cached`             |
| 7  | `runs.script`                                   |
| 8  | Inputs, groups, `runs.find`                     |
| 9  | `cluster.submit`                                |
| 10 | CLI, template, and a first real project         |

**How the tests are written:**

- TPs 0–5: tests are provided.
- TPs 6–7: behaviours are given, and you write the tests.
- TPs 8 onwards: you write the tests and part of the specification.