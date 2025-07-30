[![Python package](https://github.com/uqbar-project/wollok-jupyter-kernel/actions/workflows/test.yml/badge.svg)](https://github.com/uqbar-project/wollok-jupyter-kernel/actions/workflows/test.yml)

<img src="https://github.com/user-attachments/assets/ca46741f-f499-4dfe-a594-481926c9d1f7" alt="Wollok Jupyter Logo" height="100px" width="85px">

## Wollok Kernel for Jupyter notebook

`wollok_kernel` is a Jupyter kernel implementation, started from [a wrapper kernel](http://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html).

<img src="https://github.com/user-attachments/assets/377221a0-45b6-4f81-b63c-0f1681008922" alt="Wollok Kernel Demo">

## 💻 Installation

### Pre-requisites

You need to install **Python** (3.7 or newer). If you don't have Python, the recommended option is installing it using the [official site](https://www.python.org/downloads/), and click on `Download Python X.X.X` (there a different options depending on your operating system).

```bash
python --version
```

If `python3 --version` works, you should use an alias or replace python with python3.

Install [Conda](https://anaconda.org/anaconda/conda) environment manager. Follow [the instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) for your operating system.

Install [Node & npm](https://nodejs.org/en/download) tools.

### Wollok Kernel

Clone this repository:

```bash
git clone https://github.com/uqbar-project/wollok-jupyter-kernel # you can also use git@... option
```

Install Wollok Jupyter Kernel:

```bash
cd ./wollok-jupyter-kernel
conda init
./install_kernel.sh
```

At the end of the script you should see an output similar to the following:

```bash
Available kernels:
  python3    /path/to/venv/lib/python3.13/site-packages/ipykernel/resources
  wollok     /path/to/wollok-jupyter-kernel/venv/share/jupyter/kernels/wollok
```

If you need you can uninstall the kernel by running

```bash
./uninstall_kernel.sh
```

### VSCode

Install Jupyter extension in VSCode:

- Open Extension Tab (⇧⌘X or Ctrl+Shift+X)
- Look for "Jupyter"
- (Recommended) Install Wollok LSP extension
- Install Microsoft official extension

![Install VSCode extension](https://github.com/user-attachments/assets/5af3f097-d1ad-483a-baad-6ce40d45afe1)

Then you can create a New File... > Jupyter Notebook

![New Jupyter Notebook File](https://github.com/user-attachments/assets/986e6662-58c7-4617-acb1-9e38d0606d00)

And select kernel: click on the Kernel link at the right side > **Select another kernel** > **Jupyter Kernel** > **Wollok**:

![demoWollokJupyter](https://github.com/user-attachments/assets/4c2b7d9a-dbe3-4a5e-87b7-d553b1c6b831)

> Make sure you don't select `Python Environment` because this will expect a Python kernel, not a Wollok kernel.

## 👩‍💻 Contribution

- If you want to collaborate, follow the [developer instructions](https://github.com/uqbar-project/wollok-jupyter-kernel/wiki/Developer-environment). There's also a [main architecture explanation](https://github.com/uqbar-project/wollok-jupyter-kernel/wiki/Main-architecture)
- You can also [join the Discord channel!](https://discord.gg/ZstgCPKEaa)
- Additional info is available at the [wiki](https://github.com/uqbar-project/wollok-jupyter-kernel/wiki)

## 🦄 Using Wollok kernel

- **Notebook**: The *New* menu in the notebook should show an option for a Wollok notebook.
- **Console frontends**: To use it with the console frontends, add ``--kernel wollok`` to their command line arguments.

## ☁️ Using Wollok Kernel online

You can use [this project](https://github.com/fdodino/wollok-binder-example?tab=readme-ov-file) as an example on how to use the Wollok kernel in **MyBinder** site, a Jupyter Notebook environment in the cloud. It will use the latest stable version of the Wollok kernel based on [PyPI repository](https://pypi.org/project/wollok-kernel/).

Click on the `Launch binder` icon, wait for the environment to be ready, and you should see a Jupyter notebook with the Wollok kernel selected.

#### Powered by [Uqbar](https://uqbar.org/)
