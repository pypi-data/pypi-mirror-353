from setuptools import setup, find_packages
from pathlib import Path

long_desc = Path("README.md").read_text(encoding="utf-8")

setup(
    name="co2_emissions_ml",
    version="1.0.1",
    description="End-to-end ML pipeline for vehicle CO2 emissions prediction",
    author="Shashvat Jain",
    author_email="20je0897@mc.iitism.ac.in",
    url="https://github.com/Shashvat-Jain/CO2-predictions-using-Automotive-Features/",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_desc,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "numpy>=1.23",
        "pandas>=1.5",
        "scipy>=1.7.0",
        "scikit-learn>=1.2",
        "matplotlib>=3.5",
        "seaborn>=0.12",
        "lightgbm>=3.3",
        "xgboost>=1.7",
        "catboost>=1.1",
        "optuna>=3.0",
        "shap>=0.40",
        "jupyterlab>=3.6",
    ],
    entry_points={
        "console_scripts": [
            "run_co2=co2_emissions_ml.pipeline:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)
