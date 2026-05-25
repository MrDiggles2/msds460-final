# MSDS460 Final Project

## Getting Started

This project requires a few prequisites:

* Python version 3.11+
* [Poetry](https://python-poetry.org/docs/#installation)

### Installation

After installing the prerequisites, set up the project environment by running:

```bash
poetry install
```

### Running a Simulation

You can run a simulation using the naive first-fit placement policy with:

```bash
poetry run simulation \
  -n 100 \
  --vm-count 1000 \
  --server-count 10 \
  --policy first_fit
```

#### Notes
* `-n` controls the number of simulation runs
* `--vm-count` specifies the number of virtual machines
* `--server-count` specifies the number of servers
* `--policy` selects the placement strategy (e.g., first_fit)
