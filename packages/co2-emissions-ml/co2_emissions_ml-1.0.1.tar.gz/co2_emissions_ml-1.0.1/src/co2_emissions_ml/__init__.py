# src/__init__.py

"""
co2_emissions_ml

A Python package for end-to-end CO₂ emissions prediction from vehicle features,
including preprocessing, model training, evaluation, and prediction pipelines.
"""

__version__ = "1.0.0"

# Expose main pipeline function at package level
from .pipeline import run_pipeline
