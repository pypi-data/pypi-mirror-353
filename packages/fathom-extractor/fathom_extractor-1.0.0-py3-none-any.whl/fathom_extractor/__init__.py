"""
Fathom Extractor - Extract transcripts from HAR files

A Python tool for extracting transcripts from HAR (HTTP Archive) files,
particularly optimized for Fathom video call transcripts.
"""

from .extractor import HARTranscriptExtractor

__version__ = "1.0.0"
__author__ = "Isaac Harrison Gutekunst"
__email__ = "isaac@gutekunst.com"

__all__ = ["HARTranscriptExtractor"] 