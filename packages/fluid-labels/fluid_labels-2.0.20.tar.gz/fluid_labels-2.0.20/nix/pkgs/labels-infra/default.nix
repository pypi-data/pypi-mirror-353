{ inputs', pkgs }:
pkgs.writeShellApplication {
  bashOptions = [ "errexit" "nounset" "pipefail" ];
  name = "labels-infra";
  runtimeInputs = [
    inputs'.shell-helpers.packages.helper-aws

    pkgs.terraform
    pkgs.tflint
  ];
  text = ''
    # shellcheck disable=SC1091
    source "${./main.sh}" "$@"
  '';
}
