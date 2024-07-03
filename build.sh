#!/bin/bash

name=cv_leschultz.pdf
outdir=output

rm -rf ${outdir} ${name}

mkdir -p ${outdir}
latexmk -pdf -jobname=${outdir}/main main.tex
mv ${outdir}/main.pdf ${name}

rm -rf ${outdir}

xdg-open ${name}
