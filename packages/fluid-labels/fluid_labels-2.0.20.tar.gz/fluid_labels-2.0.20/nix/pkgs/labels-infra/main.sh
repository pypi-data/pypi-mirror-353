# shellcheck shell=bash

function _init {
  local role="${1}"
  local infra="./infra/src"

  source helper-aws aws_login "${role}" "3600"

  pushd "${infra}" || return 1
}

function _apply {
  local role="prod_labels"

  _init "${role}"
  terraform init
  if test -n "${CI:-}"; then
    terraform apply -auto-approve
  else
    terraform apply
  fi
}

function _lint {
  local role="dev"

  _init "${role}"
  terraform init
  tflint --init
  tflint --recursive
}

function _plan {
  local role="dev"

  _init "${role}"
  terraform init
  terraform plan -lock=false -refresh=true
}

function main {
  local action="${1:-}"

  case "${action}" in
    apply) _apply ;;
    lint) _lint ;;
    plan) _plan ;;
    *)
      echo "Usage: labels-infra <apply|lint|plan>"
      return 1
      ;;
  esac
}

main "${@}"
