#!/usr/bin/env python
# Created by "Thieu" at 16:08, 03/05/2025 ----------%
#       Email: nguyenthieu2102@gmail.com            %
#       Github: https://github.com/thieu1995        %
# --------------------------------------------------%

import setuptools
import os
import re


with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()


def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'probnet', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", init_content, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def readme():
    with open('README.md', encoding='utf-8') as f:
        res = f.read()
    return res


setuptools.setup(
    name="probnet",
    version=get_version(),
    author="Thieu",
    author_email="nguyenthieu2102@gmail.com",
    description="ProbNet: A Unified Probabilistic Neural Network Framework for Classification and Regression Tasks",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords=[
        "Probabilistic Neural Network", "PNN", "General Regression Neural Network",
        "GRNN", "Regression", "Supervised Learning", "Gaussian function",
        "Kernel-based Models", "Gaussian Kernel", "Non-parametric Learning",
        "multi-input multi-output (MIMO)",
        "hybrid learning", "vectorized implementation", "interpretable learning", "explainable AI (XAI)",
        "Python Library", "Machine Learning Framework", "Model Deployment", "Neural Network API",
        "machine learning", "regression", "classification", "time series forecasting",
        "soft computing", "computational intelligence", "intelligent systems",
        "Scikit-learn Compatible", "Lightweight ML Library", "Extendable Neural Networks",
        "Interpretable Machine Learning", "Plug-and-Play ML Models", "Fast Model Prototyping",
        "intelligent decision system", "adaptive system", "simulation studies"
    ],
    url="https://github.com/thieu1995/ProbNet",
    project_urls={
        'Documentation': 'https://probnet.readthedocs.io/',
        'Source Code': 'https://github.com/thieu1995/ProbNet',
        'Bug Tracker': 'https://github.com/thieu1995/ProbNet/issues',
        'Change Log': 'https://github.com/thieu1995/ProbNet/blob/main/ChangeLog.md',
        'Forum': 'https://t.me/+fRVCJGuGJg1mNDg1',
    },
    packages=setuptools.find_packages(exclude=['tests*', 'examples*']),
    include_package_data=True,
    license="GPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Benchmark",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": ["pytest==7.1.2", "pytest-cov==4.0.0", "flake8>=4.0.1"],
    },
    python_requires='>=3.8',
)
