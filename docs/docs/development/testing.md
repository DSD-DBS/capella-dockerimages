<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Local testing

## Run all tests

To run all tests, you can use the Make target:

```bash
make test
```

## Run a specific test

To run specific tests, you have to set some environment variables and you can
use the `pytest` command:

```bash
export CAPELLA_VERSION="6.0.0"
pytest -o log_cli=true -s -k "name_of_test"
```
