# toit

toit (*T*he *O*VS *I*ntegration *T*estsuite) is an integration test framework for Open vSwitch.

---

## Running the Tests

Refer to the [quickstart guide] for information on running tests.

---

## Adding Your Own Tests

It's possible to write your own tests and load them using the `--test-dir` parameter. To do this, I suggest reworking an existing test.

---

## Running Module Sample Code

As mentioned in the [design document], most of the sample applications contain some sample code. To run this, you may need to run the module from the root than the actual directory to prevent import errors. You can do this like so:

```bash
python -m trafficgens/dummy
```

---

[design document]: docs/design.md
[quickstart guide]: docs/quickstart.md
