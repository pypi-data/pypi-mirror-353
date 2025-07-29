{ libGit, makePythonEnvironment, makeTemplate, inputs, projectPath, outputs
, makeSearchPaths, ... }:
let
  labelsPythonEnv = makePythonEnvironment {
    pythonProjectDir = projectPath "/labels";
    pythonVersion = "3.11";
    overrides = _self: super: {
      cyclonedx-python-lib = super.cyclonedx-python-lib.overridePythonAttrs
        (old: {
          preUnpack = ''
            export HOME=$(mktemp -d)
            rm -rf /homeless-shelter
          '' + (old.preUnpack or "");
          # Skip https://github.com/nix-community/poetry2nix/blob/master/overrides/default.nix#L588
          postPatch = "echo Skipping postPatch";
        });
    };
  };
in {
  jobs."/labels/env" = makeTemplate {
    name = "labels-pypi-env";
    replace = { __argSrcLabels__ = projectPath "/labels"; };
    searchPaths = {
      pythonPackage = [ (projectPath "/labels") ];
      source = [
        libGit
        labelsPythonEnv
        (makeTemplate {
          replace = {
            __argSrcTreeSitterParsers__ =
              outputs."/labels/env/tree-sitter-patch";
          };
          name = "labels-config-context-file";
          template = ''
            export TREE_SITTER_PARSERS_DIR='__argSrcTreeSitterParsers__'
            export BUGSNAG_API_KEY=82c9f090e2049a63c44a2045b029a7a8
          '';
        })
      ];
      bin = [ inputs.nixpkgs.skopeo ];
    };
    template = ./template.sh;
  };
}
