{ lib', pkgs }:
pkgs.writeShellApplication {
  bashOptions = [ "errexit" "nounset" "pipefail" ];
  name = "labels-lint";
  runtimeInputs = lib'.envs.labels.dependencies.editable;
  text = ''
    pushd "''${1:-.}"

    if test -n "''${CI:-}"; then
      ruff format --config ruff.toml --diff
      ruff check --config ruff.toml
    else
      ruff format --config ruff.toml
      ruff check --config ruff.toml --fix
    fi

    mypy --config-file mypy.ini labels
    mypy --config-file mypy.ini test
  '';
}
