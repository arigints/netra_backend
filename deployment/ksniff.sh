#!/bin/bash

wget https://github.com/eldadru/ksniff/releases/download/v1.6.2/ksniff.zip
unzip ksniff.zip
sed -i 's/--short=true //' /app/Makefile
make install