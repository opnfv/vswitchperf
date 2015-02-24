# Getting Started with 'toit'

Running tests with toit is easy - there are only two steps required after [installation]:

1. Configure your own `settings.py` file
2. Execute tests using this custom `settings.py` file

---

## Creating a custom `settings.py` file

You should create your own `settings.py` file, based on the `default_settings.py` file found in the `toit.conf` package. This file should contain versions of all variables found in `default_settings.py` where you wish to override them. For example, should you wish to override just the `RTE_SDK` parameter then this would be a valid `settings.py` file.

```python
# my custom settings file

RTE_SDK = '/home/username/src/dpdk'
```

The custom settings file is passed to `run` via the `--conf-file` argument.

```bash
./run --conf-file=<path_to_settings_py> <test_spec>
```

Note that configuration passed in via the environment (`--load-env`) or via another command line argument will override both the default and your custom configuration files. This "priority hierarchy" can be described like so (1 = max priority):

1. Command line arguments
2. Environment variables
3. Configuration file(s)

---

## Executing tests

Everything is run using the aptly named `run` executable.

To list the available tests:

```bash
./run --list
```

To run a group of tests (a module):

```bash
./run dpdkport
```

To run a single test:

```bash
./run dpdkport.AddPort
```

Some tests allow for configurable parameters, including test duration (in seconds) as well as packet sizes (in bytes).

```bash
./run --test-dir tests-vswitchperf
    --test-param 'rfc2544_duration=10;packet_sizes=128'
    --conf-file /home/$USER/toit_conf.py
```

For all available options, check out the help dialog:

```bash
./run --help
```

---

[installation]: installation.md

