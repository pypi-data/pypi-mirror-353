# PyLWL: A Python Framework for Locally Weighted Learning

[![GitHub release](https://img.shields.io/badge/release-0.2.0-yellow.svg)](https://github.com/thieu1995/PyLWL/releases)
[![PyPI version](https://badge.fury.io/py/pylwl.svg)](https://badge.fury.io/py/pylwl)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pylwl.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pylwl.svg)
[![Downloads](https://pepy.tech/badge/pylwl)](https://pepy.tech/project/pylwl)
[![Tests & Publishes to PyPI](https://github.com/thieu1995/PyLWL/actions/workflows/publish-package.yml/badge.svg)](https://github.com/thieu1995/PyLWL/actions/workflows/publish-package.yml)
[![Documentation Status](https://readthedocs.org/projects/pylwl/badge/?version=latest)](https://pylwl.readthedocs.io/en/latest/?badge=latest)
[![Chat](https://img.shields.io/badge/Chat-on%20Telegram-blue)](https://t.me/+fRVCJGuGJg1mNDg1)
[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.29089784-blue)](https://doi.org/10.6084/m9.figshare.29089784)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## 📌 Overview

**PyLWL** is an open-source Python library that provides a unified, extensible, and user-friendly 
implementation of *Locally Weighted Learning* (LWL) algorithms for supervised learning.
It implements differentiable and gradient-descent-based local models for both classification and regression tasks.

## Features

- 📌 **GdLwClassifier**: Local weighted classifier using logistic regression with support for binary and multiclass classification.
- 📌 **GdLwRegressor**: Local weighted regressor using linear regression optimized with MSE loss.
- 📌 **LwClassifier** and **LwRegressor**: Local weighted classifier/regressor with a fixed kernel.
- 🧠 Supports any **differentiable kernel function** (e.g., Gaussian, Epanechnikov).
- ⚙️ Built with **PyTorch**, and fully compatible with **Scikit-Learn** pipeline and metrics.
- 🔧 Configurable optimizer (`Adam`, `SGD`, etc.) and hyperparameters.
- 🔍 Built-in support for model evaluation and scoring.


## 📖 Citation Request 

Please include these citations if you plan to use this library:

```bibtex
@software{thieu20250517PyLWL,
  author       = {Nguyen Van Thieu},
  title        = {PyLWL: A Python Framework for Locally Weighted Learning},
  month        = June,
  year         = 2025,
  doi         = {10.6084/m9.figshare.29089784},
  url          = {https://github.com/thieu1995/PyLWL}
}
```

## 📦 Installation

Install the latest version from PyPI:

```bash
pip install pylwl
```

Verify installation:

```sh
$ python
>>> import pylwl
>>> pylwl.__version__
```

## 🚀 Quick Start


### Classification

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from pylwl import LwClassifier

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Train LVQ1 model
model = LwClassifier(kernel="gaussian", tau=1.0)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", model.score(X_test, y_test))
```

### Regression

```python
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from pylwl import LwRegressor

X, y = fetch_california_housing(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

reg = LwRegressor(kernel='gaussian', tau=1.0)
reg.fit(X_train, y_train)
print("R2 score:", reg.score(X_test, y_test))
```

Please read the [examples](/examples) folder for more use cases.


## 📚 Documentation

Documentation is available at: 👉 https://pylwl.readthedocs.io

You can build the documentation locally:

```shell
cd docs
make html
```

## 🧪 Testing
You can run unit tests using:

```shell
pytest tests/
```

## 🤝 Contributing
We welcome contributions to `PyLWL`! If you have suggestions, improvements, or bug fixes, feel free to fork 
the repository, create a pull request, or open an issue.


## 📄 License
This project is licensed under the GPLv3 License. See the LICENSE file for more details.


## 📎 Official channels 

* 🔗 [Official source code repository](https://github.com/thieu1995/PyLWL)
* 📘 [Official document](https://pylwl.readthedocs.io/)
* 📦 [Download releases](https://pypi.org/project/pylwl/) 
* 🐞 [Issue tracker](https://github.com/thieu1995/PyLWL/issues) 
* 📝 [Notable changes log](/ChangeLog.md)
* 💬 [Official discussion group](https://t.me/+fRVCJGuGJg1mNDg1)

---

Developed by: [Thieu](mailto:nguyenthieu2102@gmail.com?Subject=GrafoRVFL_QUESTIONS) @ 2025
