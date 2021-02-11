#!/bin/bash
cd ..
python3 setup.py docs
rsync -r docs/_build/html/* monkeypaw:/home/morelandjs/sportquery_docs
