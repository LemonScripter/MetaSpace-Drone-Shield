#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import codecs

# Olvasd be a fájlt latin-1 kódolással (ami gyakran okozza a problémát)
with open('index.html', 'r', encoding='latin-1') as f:
    content = f.read()

# Írd ki UTF-8 kódolással
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fájl újrakódolva UTF-8-ra")

