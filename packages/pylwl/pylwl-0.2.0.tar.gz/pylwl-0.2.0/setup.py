#!/usr/bin/env python
# Created by "Thieu" at 13:29, 10/05/2025 ----------%
#       Email: nguyenthieu2102@gmail.com            %
#       Github: https://github.com/thieu1995        %
# --------------------------------------------------%

import setuptools
import os
import re


with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()


def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'pylwl', '__init__.py')
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
    name="pylwl",
    version=get_version(),
    author="Thieu",
    author_email="nguyenthieu2102@gmail.com",
    description="PyLWL: A Python Framework for Locally Weighted Learning",
    long_description=readme(),
    long_description_content_type="text/markdown",
    keywords = [
        "Locally Weighted Learning", "Gradient Descent", "Instance-Based Learning",
        "Nonparametric Models", "Local Models", "PyTorch",
        "Machine Learning", "Classification", "Regression",
        "Supervised Learning", "Adaptive Models", "Distance-Based Learning",
        "Kernel Methods", "Weighted Loss", "Local Approximation",
        "Model Training", "Python Framework", "Neural Network",
        "Bias-Free Models", "Sample-Weighted Optimization",
        "Open-source Machine Learning", "Model Interpretability",
        "Gradient Descent Optimization", "Model Wrapping",
        "Benchmarking", "machine learning", "artificial intelligence",
        "generalization", "model selection", "Cross-validation",
        "automl", "parameter search", "search algorithm",
        "optimization framework", "global optimization", "local optimization",
        "Computational intelligence", "Robust optimization"],
    url="https://github.com/thieu1995/PyLWL",
    project_urls={
        'Documentation': 'https://pylwl.readthedocs.io/',
        'Source Code': 'https://github.com/thieu1995/PyLWL',
        'Bug Tracker': 'https://github.com/thieu1995/PyLWL/issues',
        'Change Log': 'https://github.com/thieu1995/PyLWL/blob/main/ChangeLog.md',
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
