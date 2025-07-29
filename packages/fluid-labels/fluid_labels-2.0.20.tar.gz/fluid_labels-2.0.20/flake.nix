{
  description = "Fluid Attacks SBOM Library";

  inputs = {
    flake-parts.url =
      "github:hercules-ci/flake-parts/f4330d22f1c5d2ba72d3d22df5597d123fdb60a9?shallow=1";
    nixpkgs.url =
      "github:nixos/nixpkgs/ab472a7a8fcfd7c778729e7d7c8c3a9586a7cded?shallow=1";

    pipeline = {
      inputs.flake-parts.follows = "flake-parts";
      url =
        "gitlab:fluidattacks/universe/06afc68c86a9686214b246e2a69276b061f08091?shallow=1&dir=common/utils/pipeline";
    };
    python-env = {
      inputs.flake-parts.follows = "flake-parts";
      url =
        "gitlab:fluidattacks/universe/06afc68c86a9686214b246e2a69276b061f08091?shallow=1&dir=common/utils/python-env";
    };
    shell-helpers = {
      inputs = {
        flake-parts.follows = "flake-parts";
        nixpkgs.follows = "nixpkgs";
      };
      url =
        "gitlab:fluidattacks/universe/06afc68c86a9686214b246e2a69276b061f08091?shallow=1&dir=common/utils/shell-helpers";
    };
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      debug = false;

      systems = [ "aarch64-darwin" "aarch64-linux" "x86_64-linux" ];

      perSystem = { inputs', pkgs, self', system, ... }:
        let
          projectPath = path: ./. + path;
          lib' = {
            envs = import ./nix/envs { inherit inputs pkgs projectPath; };
            pipeline = inputs.pipeline.lib { inherit pkgs; };
            inherit projectPath;
          };
        in {
          _module.args.pkgs = import inputs.nixpkgs {
            inherit system;
            config.allowUnfree = true;
          };

          apps = import ./nix/apps.nix { inherit pkgs self'; };
          devShells = import ./nix/shells.nix { inherit lib' pkgs self'; };
          packages = import ./nix/pkgs { inherit inputs' lib' pkgs self'; };
        };
    };
}
