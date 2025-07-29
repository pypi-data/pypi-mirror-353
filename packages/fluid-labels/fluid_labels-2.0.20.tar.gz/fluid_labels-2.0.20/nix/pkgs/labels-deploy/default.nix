{ inputs', lib', pkgs }:
pkgs.writeShellApplication {
  name = "labels-deploy";
  runtimeInputs = pkgs.lib.flatten [
    lib'.envs.labels.dependencies.default
    inputs'.shell-helpers.packages.helper-aws
    inputs'.shell-helpers.packages.helper-sops
    pkgs.uv
  ];
  text = ''
    if ! git diff HEAD~1 HEAD -- pyproject.toml | grep -q '^[-+]version'; then
      echo "[INFO] pyproject.toml version has not changed. Skipping deployment."
      exit 0
    fi

    # shellcheck disable=SC1091
    source helper-aws aws_login "dev" "3600"

    # Load secrets
    secrets=(
       PYPI_API_TOKEN_FLUID_LABELS
      )
    # shellcheck disable=SC1091
    source helper-sops sops_export_vars "secrets/dev.yaml" "''${secrets[@]}"

    echo "Publishing new version for labels"
    rm -rf "dist"
    uv build
    uv publish --token "''${PYPI_API_TOKEN_FLUID_LABELS}"
  '';
  bashOptions = [ "errexit" "nounset" "pipefail" ];
}
