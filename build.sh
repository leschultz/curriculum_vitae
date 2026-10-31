#!/usr/bin/env bash
# Build from any working directory. Publish the PDF only after all passes succeed.
set -Eeuo pipefail

preview=false
case "${1:-}" in
    "") ;;
    --open) preview=true ;;
    --help|-h)
        printf 'Usage: %s [--open]\nRequires XeLaTeX, Biber, and the packages listed in README.md.\n' "$0"
        exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
esac
if (( $# > 1 )); then
    printf 'Expected at most one option. Use --help for usage.\n' >&2
    exit 2
fi

for tool in xelatex biber; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        printf 'Missing dependency: %s. See README.md for installation instructions.\n' "$tool" >&2
        exit 1
    fi
done

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$root"
mkdir -p -- "$root/.build"
work="$(mktemp -d "$root/.build/run.XXXXXX")"
log="$work/build.log"
trap 'printf "Build failed. Diagnostics: %s\n" "$log" >&2' ERR

run() {
    "$@" >>"$log" 2>&1
}
tex=(xelatex -interaction=nonstopmode -halt-on-error -file-line-error -no-shell-escape "-output-directory=$work" main.tex)
printf 'Building CV with XeLaTeX and Biber…\n'
run "${tex[@]}"
run biber --input-directory "$work" --output-directory "$work" main
run "${tex[@]}"
run "${tex[@]}"
test -s "$work/main.pdf"
mv -- "$work/main.pdf" "$root/cv_full_leschultz.pdf"
trap - ERR
printf 'Built %s\nDiagnostics: %s\n' "$root/cv_full_leschultz.pdf" "$log"

if "$preview"; then
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$root/cv_full_leschultz.pdf"
    elif command -v open >/dev/null 2>&1; then
        open "$root/cv_full_leschultz.pdf"
    else
        printf 'PDF built successfully; no supported preview application was found.\n'
    fi
fi
