# shellcheck shell=bash

function main {
  local secrets="${1}"
  local resolver_directory_name="${2:-}"
  local pytest_args=(
    --disable-warnings
    --showlocals
    -vv
  )

  source labels-envars
  source helper-aws aws_login "dev" "3600"
  source helper-sops sops_export_vars "${secrets}" AWS_EXTERNAL_ID AWS_TEST_ROLE

  echo "Executing tests for: ${resolver_directory_name}"

  pytest test/functional/"${resolver_directory_name}" "${pytest_args[@]}"
}

main "${@}"
