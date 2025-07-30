# Jupyter libyt

[![PyPI version](https://badge.fury.io/py/jupyter-libyt.svg)](https://badge.fury.io/py/jupyter-libyt)

This is a Jupyter provisioner for [`libyt`](https://github.com/yt-project/libyt) kernel.

- **Jupyter Project**: https://jupyter.org/
- **yt**: https://yt-project.org/
- **libyt Repo**: https://github.com/yt-project/libyt
- **libyt Doc**: https://libyt.readthedocs.io/en/latest/

### Install

- From PyPI:
  ```bash
  pip install jupyter-libyt
  ```
- From source:
  ```bash
  git clone https://github.com/yt-project/jupyter_libyt.git
  cd jupyter_libyt
  jlpm install      # make sure JupyterLab is already installed
  jlpm run build
  pip install .
  ```

### Uninstall

```bash
# uninstall the package
pip uninstall jupyter-libyt

# remove the kernelspec folder
rm -rf $<python-prefix>/share/jupyter/kernels/libyt_kernel
```

### Change Log

#### 0.3.0

- Nothing changed, version bumped to match `libyt`/`yt_libyt`.

#### 0.2.0

- Drop support for Python 3.7.
- Support JupyterLab >= 4.0.0 and Jupyter Notebook >= 7.0.0.
- Add the frontend:
  - Send notification and block it when `interrupt`/`restart`/`restart and run all` buttons are
    clicked to avoid unwanted action showing.
  - Send notification and block it when the interrupt and restart kernel menu are clicked to avoid
    unwanted action showing.

#### 0.1.0

- Provide only the kernel provisioner for libyt kernel.
