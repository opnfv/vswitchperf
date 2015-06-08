# Getting Started with 'vsperf'

## Installation

Follow the [installation instructions] to install.

---

## Configure the `./conf/10_custom.conf` file

The supplied `10_custom.conf` file must be modified, as it contains
configuration items for which there are no reasonable default values.

The configuration items that can be added is not limited to the initial
contents. Any configuration item mentioned in any .conf file in `./conf`
directory can be added and that item will be overridden by the custom
configuration value.


## Using a custom settings file

Alternatively a custom settings file can be passed to `vsperf` via the
`--conf-file` argument.

```bash
./vsperf --conf-file <path_to_settings_py> ...
```

Note that configuration passed in via the environment (`--load-env`) or via
another command line argument will override both the default and your custom
configuration files. This "priority hierarchy" can be described like so (1 =
max priority):

1. Command line arguments
2. Environment variables
3. Configuration file(s)

---

## Executing tests

To list the available tests:

```bash
./vsperf --list-tests
```

To run a group of tests, for example all tests with a name containing
'RFC2544':

```bash
./vsperf --conf-file=user_settings.py --tests="RFC2544"
```

To run all tests:

```bash
./vsperf --conf-file=user_settings.py
```

Some tests allow for configurable parameters, including test duration (in
seconds) as well as packet sizes (in bytes).

```bash
./vsperf --conf-file user_settings.py
    --tests RFC2544Tput
    --test-param "rfc2544_duration=10;packet_sizes=128"
```

For all available options, check out the help dialog:

```bash
./vsperf --help
```

---

[installation instructions]: installation.md

