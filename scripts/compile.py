#!/usr/bin/env python3
from pathlib import Path
from evokb.retriever import compile_to_wiki

for f in Path("raw").glob("*.md"):
    compile_to_wiki(f, Path("wiki"))
