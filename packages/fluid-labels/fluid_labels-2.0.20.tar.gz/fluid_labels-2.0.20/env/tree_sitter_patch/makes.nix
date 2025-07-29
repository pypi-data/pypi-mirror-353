{ inputs, ... }:
let
  treeSitterSwift = builtins.fetchTarball {
    url =
      "https://github.com/alex-pinkus/tree-sitter-swift/archive/57c1c6d6ffa1c44b330182d41717e6fe37430704.tar.gz";
    sha256 = "sha256:18z9rlycls841qvjgs376kqnwds71sm6lbafgjk8pxfqa7w6gwqn";
  };
  tree-sitter = inputs.nixpkgs.python311Packages.tree-sitter.overridePythonAttrs
    (oldAttrs: {
      src = inputs.nixpkgs.fetchFromGitHub {
        owner = "tree-sitter";
        repo = "py-tree-sitter";
        rev = "refs/tags/v0.21.1";
        sha256 = "sha256-U4ZdU0lxjZO/y0q20bG5CLKipnfpaxzV3AFR6fGS7m4=";
        fetchSubmodules = true;
      };
      dependencies = [ inputs.nixpkgs.python311Packages.setuptools ];
    });
in {
  jobs."/labels/env/tree-sitter-patch" = inputs.nixpkgs.stdenv.mkDerivation {
    buildPhase = ''
      export envTreeSitterSwift="${treeSitterSwift}"

      python build.py
    '';
    name = "labels-env-tree-sitter-patch";
    nativeBuildInputs = [ tree-sitter ];
    src = ./.;
  };
}
