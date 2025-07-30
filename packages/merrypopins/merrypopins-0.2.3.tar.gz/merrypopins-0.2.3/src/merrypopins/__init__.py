"""
merrypopins
===========

A modular pipeline for nanoindentation analysis. Includes tools for:

 - `load_datasets`: Load raw indentation `.txt` and their metadata `.tdm` files into pandas DataFrames.
 - `preprocess`: Clean and normalize indentation data, apply contact point detection.
 - `locate`: Detect pop-in events using methods such as IsolationForest, CNN, Savitzky-Golay, and Finite Differences.
 - `statistics`: Analyze and visualize statistical distributions of pop-in events.
 - `make_dataset`: Construct enriched datasets by running the full pipeline and exporting annotated results and visualizations.
"""

__version__ = "0.2.3"

# Expose submodules at the package level
from . import load_datasets, preprocess, locate, statistics, make_dataset

# Define what 'from merrypopins import *' exposes
__all__ = [
    "load_datasets",
    "preprocess",
    "locate",
    "statistics",
    "make_dataset",
]
