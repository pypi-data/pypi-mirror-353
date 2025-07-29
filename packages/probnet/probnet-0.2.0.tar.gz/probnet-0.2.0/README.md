# ProbNet: A Unified Probabilistic Neural Network Framework for Classification and Regression Tasks

[![GitHub release](https://img.shields.io/badge/release-0.2.0-yellow.svg)](https://github.com/thieu1995/ProbNet/releases)
[![PyPI version](https://badge.fury.io/py/probnet.svg)](https://badge.fury.io/py/probnet)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/probnet.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/probnet.svg)
[![Downloads](https://pepy.tech/badge/probnet)](https://pepy.tech/project/probnet)
[![Tests & Publishes to PyPI](https://github.com/thieu1995/ProbNet/actions/workflows/publish-package.yml/badge.svg)](https://github.com/thieu1995/ProbNet/actions/workflows/publish-package.yml)
[![Documentation Status](https://readthedocs.org/projects/probnet/badge/?version=latest)](https://probnet.readthedocs.io/en/latest/?badge=latest)
[![Chat](https://img.shields.io/badge/Chat-on%20Telegram-blue)](https://t.me/+fRVCJGuGJg1mNDg1)
[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.28802531-blue)](https://doi.org/10.6084/m9.figshare.28802435)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


---

## 🌟 Overview

**ProbNet** is a lightweight and extensible Python library that provides a unified implementation of 
**Probabilistic Neural Network (PNN)** and its key variant, the **General Regression Neural Network (GRNN)**. 
It supports both **classification** and **regression** tasks, making it suitable for a wide range of 
supervised learning applications.

---

## 🔧 Features

- 🧠 Full implementation of PNN for classification
- 📈 GRNN for regression modeling
- 🔍 Scikit-learn compatible interface (`fit`, `predict`, `score`)
- 🔄 Built-in support for many kernels and distance metrics
- 🧪 Fast prototyping and evaluation
- 🧩 Easily extendable and readable codebase
- 📚 Auto-generated documentation with Sphinx 
- Probabilistic models: `PnnClassifier`, `GrnnRegressor`
---

## 📖 Citation Request 

Please include these citations if you plan to use this library:

```bibtex
@software{thieu20250503,
  author       = {Nguyen Van Thieu},
  title        = {ProbNet: A Unified Probabilistic Neural Network Framework for Classification and Regression Tasks},
  month        = may,
  year         = 2025,
  doi         = {10.6084/m9.figshare.28802435},
  url          = {https://github.com/thieu1995/ProbNet}
}
```

## 📦 Installation

Install the latest version using pip:

```bash
pip install probnet
```

After installation, check the version to ensure successful installation:

```sh
$ python
>>> import probnet
>>> probnet.__version__
```

## 🚀 Quick Start

For Classification using PNN:

```python
from probnet import PnnClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = PnnClassifier(sigma=0.1)
model.fit(X_train, y_train)
print("Accuracy:", model.score(X_test, y_test))
```

For Regression using GRNN:

```python
from probnet import GrnnRegressor
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = GrnnRegressor(sigma=0.5)
model.fit(X_train, y_train)
print("R2 Score:", model.score(X_test, y_test))
```

## 📚 Documentation

Documentation is available at: 👉 https://probnet.readthedocs.io

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
We welcome contributions to `ProbNet`! If you have suggestions, improvements, or bug fixes, feel free to fork 
the repository, create a pull request, or open an issue.


## 📄 License
This project is licensed under the GPLv3 License. See the LICENSE file for more details.


## 📎 Official channels 

* 🔗 [Official source code repository](https://github.com/thieu1995/ProbNet)
* 📘 [Official document](https://probnet.readthedocs.io/)
* 📦 [Download releases](https://pypi.org/project/probnet/) 
* 🐞 [Issue tracker](https://github.com/thieu1995/ProbNet/issues) 
* 📝 [Notable changes log](/ChangeLog.md)
* 💬 [Official discussion group](https://t.me/+fRVCJGuGJg1mNDg1)

---

Developed by: [Thieu](mailto:nguyenthieu2102@gmail.com?Subject=ProbNet_QUESTIONS) @ 2025
