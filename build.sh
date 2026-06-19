#!/bin/bash

name=./cv_full_leschultz.pdf
outdir=output

rm -rf ${outdir} ${name}

mkdir -p ${outdir}
latexmk -xelatex -jobname=${outdir}/main main.tex > log.txt
mv ${outdir}/main.pdf ${name}

rm -rf ${outdir}

xdg-open ${name}
