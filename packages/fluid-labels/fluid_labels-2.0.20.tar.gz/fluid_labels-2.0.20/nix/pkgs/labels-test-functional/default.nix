{ inputs', lib', pkgs }:
pkgs.writeShellApplication {
  bashOptions = [ "errexit" "nounset" "pipefail" ];
  name = "labels-test-functional";
  runtimeInputs = pkgs.lib.flatten [
    lib'.envs.labels.dependencies.editable
    inputs'.shell-helpers.packages.helper-aws
    inputs'.shell-helpers.packages.helper-sops
    lib'.envs.labels.envars
  ];
  text = ''
    # shellcheck disable=SC1091
    source "${./main.sh}" \
    "${lib'.projectPath "/secrets/dev.yaml"}" \
    "$@"
  '';
}
