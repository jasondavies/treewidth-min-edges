"""Reuse the packaged treewidth-nine checker and independent reference code."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "nine"))
from run_treewidth_edge_checks import ROOT, CC, SOURCE, run, encode, masks, verify_order, digest
from reference import decode, width_reachable, verify_width_lower
