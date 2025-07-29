{ lib', pkgs }:
pkgs.writeShellApplication {
  bashOptions = [ "errexit" "nounset" "pipefail" ];
  name = "labels-test";
  runtimeInputs = pkgs.lib.flatten [
    lib'.envs.labels.dependencies.editable
    lib'.envs.labels.envars
  ];
  text = ''
    # shellcheck disable=SC1091
    source "${./main.sh}" \
    "$@"
  '';
}
