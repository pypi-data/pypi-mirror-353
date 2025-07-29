# shellcheck shell=bash

function main {
  local module="${1}"
  local tests=("${@:2}")
  export COVERAGE_FILE
  COVERAGE_FILE="labels/labels/.coverage.${module}"
  export PYTHONPATH="$PWD"

  source labels-envars

  pushd labels || return 1
  labels-testing --target "${module}" --tests "${tests[@]}"
}

main "${@}"
