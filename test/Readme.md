To use pytests with coverage outputs call from main-directory:

ensure first, that "coverage" is installed on your device. Therefore, start by installinc coverage:

```shell
    pip install coverage
```

then use call line-by-line to recive a test coverage report file:

```shell
    coverage run --source=src -m pytest test -vvv
    coverage xml -o coverage.xml
    coverage report
```

And then use the VS-Code Extension "Coverage Gutters" and display-coverage within the python ./src modules
