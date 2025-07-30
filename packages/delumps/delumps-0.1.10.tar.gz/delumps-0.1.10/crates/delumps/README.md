# README

Delumps is an Rust extension module for computing semantic similarity between individuals within *C2S2*,
a tool for phenotype-driven identification of disease subgroups.


## Setup

We deploy Delumps to Python Package Index (PyPi), so installation with PIP should be possible:

```shell
python3 -m pip install delumps
```

### Install in production mode

Alternatively, Delumps can be installed from sources:

```shell
cd crates/delumps  # Change to the extension directory

python3 -m pip install .
```
Note, the installation may fail if Rust toolchain is not available on your system.


### Install in development mode

For package developers, the package is installed into the active virtual environment by running:

```shell
maturin develop -E test
# or
python3 -m pip install -e .[test]
```

The package is installed in editable mode along with the `test` extras, that include Pytest and Numpy.

We can run the tests to verify that the installation went well:

```shell
pytest
```

## Use with C2S2

Delumps provides a `delumps.SimilarityMatrixCreatorFactory` 
that can create a `delumps.SimilarityMatrixCreator` to use with *C2S2*.

```python
import delumps

fpath_hpo = '/path/to/hp.json'
fpath_ic_mica = '/path/to/term-pair-similarity.csv.gz'

factory = delumps.SimilarityMatrixCreatorFactory.from_hpo_and_ic_mica(fpath_hpo, fpath_ic_mica)
```

The factory needs path to a HPO JSON file and an IC MICA file with precomputed information content (IC)
for the most informative common ancestor (MICA) term of an HPO term pair.

Then, similarity matrix creator that uses the Phenomizer semantic similarity measure can be configured
by running:

```python
phenomizer_smc = factory.create_phenomizer_smc()
```

`phenomizer_smc` can be used as a `SimilarityMatrixCreator` component of the *C2S2* framework.


## Release

We deploy Delumps to PyPi:

```shell
cd crates/delumps

maturin publish
```