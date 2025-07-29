{ inputs', lib', pkgs, self' }: {
  default = self'.packages.labels;

  labels = pkgs.callPackage ./labels { inherit lib'; };
  labels-deploy = pkgs.callPackage ./labels-deploy { inherit inputs' lib'; };
  labels-infra = pkgs.callPackage ./labels-infra { inherit inputs'; };
  labels-lint = pkgs.callPackage ./labels-lint { inherit lib'; };
  labels-pipeline = pkgs.callPackage ./labels-pipeline { inherit lib'; };
  labels-test = pkgs.callPackage ./labels-test { inherit lib'; };
  labels-test-functional =
    pkgs.callPackage ./labels-test-functional { inherit inputs' lib'; };
}
