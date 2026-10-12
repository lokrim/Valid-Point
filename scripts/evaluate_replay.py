#!/usr/bin/env python3
"""Run only R05 with existing local pinned data; never download/extract or open H."""
from pathlib import Path
import argparse
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from valid_point.evaluation.real import run_stage
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path)
    parser.add_argument('--phase',choices=('intake','predict','report','finalize','all'),default='all')
    args=parser.parse_args()
    print(run_stage(ROOT,args.run,args.phase),flush=True)
