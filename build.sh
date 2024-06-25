#!/bin/bash

name=cv_leschultz
outdir=output

mkdir -p ${outdir}
latexmk -pdf -jobname=${outdir}/${name} ${name}.tex
ln -s ${outdir}/${name}.pdf ${name}.pdf
xdg-open ${name}.pdf
