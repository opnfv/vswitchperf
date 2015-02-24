# Installing toit

The test suite relies on a number of other packages. These need to be installed for the test suite to function.

You can do this manually or via the provided [install][install-script] script.

To use the install script, simply:

```bash
./install.sh
```

Otherwise, install the requirements as specified below.

---

## System packages

There are a number of packages that must be installed using `yum`. These can be installed like so:

```bash
yum -y install $(cat packages.txt)
```

---

## Python Packages

The required Python packages can be found in the `requirements.txt` file in the root of the test suite. They can be installed like so:

```bash
pip install -r requirements.txt
```

---

# Working Behind a Proxy

If you're behind a proxy, you'll likely want to configure this before running any of the above. For example:

```bash
export http_proxy=proxy.mycompany.com:123
export https_proxy=proxy.mycompany.com:123
```

---

[install-script]: ../install.sh
