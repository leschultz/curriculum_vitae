#!/bin/bash

name=cv_leschultz.pdf
outdir=output

rm -rf ${outdir} ${name}

mkdir -p ${outdir}
latexmk -pdf -jobname=${outdir}/main main.tex
ln -s ${outdir}/main.pdf ${name}

xdg-open ${name}
