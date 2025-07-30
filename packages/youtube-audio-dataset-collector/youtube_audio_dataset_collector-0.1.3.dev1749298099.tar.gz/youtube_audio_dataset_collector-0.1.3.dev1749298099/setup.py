#!/usr/bin/env python3
"""
Setup script for YouTube Audio Dataset Collector library
"""

from setuptools import setup, find_packages
import re
import subprocess
import os
import time


def get_version():
    try:
        tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).decode().strip()
        # Remove leading 'v' if present
        if tag.startswith('v'):
            tag = tag[1:]
        if re.match(r"^\d+\.\d+\.\d+$", tag):
            return f"{tag}.dev{int(time.time())}"
    except Exception:
        pass
    return f"0.0.1.dev{int(time.time())}"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube-audio-dataset-collector",
    version=get_version(),
    author="Ranjan Shettigar",
    author_email="theloko.dev@gmail.com",
    description="A comprehensive tool for downloading, processing, and transcribing audio from YouTube videos and playlists for machine learning datasets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2023.1.6",
        "pydub>=0.25.1",
        "google-generativeai>=0.3.0",
        "python-dotenv>=0.19.0",
        "tqdm>=4.64.0",
        "numpy>=1.21.0",
        "soundfile>=0.12.1",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.910',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
            'sphinx-autodoc-typehints>=1.12',
        ],
    },
    entry_points={
        'console_scripts': [
            'youtube-audio-collector=youtube_audio_collector.cli:main',
            'yadc=youtube_audio_collector.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        'youtube', 'audio', 'dataset', 'machine-learning', 'transcription', 
        'gemini', 'speech-to-text', 'data-collection', 'ml', 'ai'
    ],
)
