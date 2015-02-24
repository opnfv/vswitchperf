# Debugging a VM

It is possible to run some modules in a standalone mode. For a QEMU instance this is achieved by running:

```bash
python -m toit/guest/qemu
```

You can then access the VM by running:

```bash
vncviewer :1
```

from another terminal.

---

