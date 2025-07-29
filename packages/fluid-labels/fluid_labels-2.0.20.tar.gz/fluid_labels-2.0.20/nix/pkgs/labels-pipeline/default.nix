{ lib', pkgs }:
let
  rules = let products = [ "labels" "all" ];
  in {
    default = lib'.pipeline.core.rules.titleRule {
      inherit products;
      types = [ ];
    };
    noRotate = lib'.pipeline.core.rules.titleRule {
      inherit products;
      types = [ "feat" "fix" "refac" ];
    };
  };

  tests = let
    listDirectories = path:
      let
        content = builtins.readDir (lib'.projectPath path);
        directories = pkgs.lib.filterAttrs
          (key: value: value == "directory" && !pkgs.lib.hasPrefix "__" key)
          content;
      in builtins.attrNames directories;
    labelsModules =
      pkgs.lib.subtractLists [ "testing" "config" ] (listDirectories "/labels");
    jobNames = builtins.map (module: "labels-test ${module}") labelsModules;
    moduleName = jobName: pkgs.lib.strings.removePrefix "labels-test " jobName;
  in pkgs.lib.attrsets.genAttrs jobNames (jobName:
    lib'.pipeline.jobs.nix {
      component = "labels";
      rules = lib'.pipeline.rules.dev ++ [ rules.noRotate ];
      script = "nix run ./labels#labels-test ${moduleName jobName}";
      stage = lib'.pipeline.stages.test;
      tags = [ lib'.pipeline.tags.aarch64 ];
    });

in lib'.pipeline.sync {
  name = "labels-pipeline";
  targetPath = ".gitlab-ci.yaml";
  pipeline = {
    "labels-infra apply" = lib'.pipeline.jobs.nix {
      component = "labels";
      resource_group = "deploy/$CI_JOB_NAME";
      rules = lib'.pipeline.rules.prod ++ [ rules.default ];
      script = "nix run .#labels-infra apply";
      stage = lib'.pipeline.stages.deploy;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
    "labels-infra lint" = lib'.pipeline.jobs.nix {
      component = "labels";
      rules = lib'.pipeline.rules.dev ++ [ rules.noRotate ];
      script = "nix run .#labels-infra lint";
      stage = lib'.pipeline.stages.test;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
    "labels-infra plan" = lib'.pipeline.jobs.nix {
      component = "labels";
      rules = lib'.pipeline.rules.dev ++ [ rules.noRotate ];
      script = "nix run .#labels-infra plan";
      stage = lib'.pipeline.stages.test;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
    labels-lint = lib'.pipeline.jobs.nix {
      cache = {
        key = "$CI_COMMIT_REF_NAME-labels-lint";
        paths = [
          "labels/.ruff_cache"
          "labels/.import_linter_cache"
          "labels/.mypy_cache"
        ];
      };
      component = "labels";
      rules = lib'.pipeline.rules.dev ++ [ rules.noRotate ];
      script = "nix run .#labels-lint";
      stage = lib'.pipeline.stages.test;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
    labels-pipeline = lib'.pipeline.jobs.nix {
      component = "labels";
      rules = lib'.pipeline.rules.dev ++ [ rules.noRotate ];
      script = "nix run .#labels-pipeline";
      stage = lib'.pipeline.stages.test;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
    "labels-test-functional reports" = lib'.pipeline.jobs.nix {
      component = "labels";
      rules = lib'.pipeline.rules.dev ++ [ rules.noRotate ];
      script = "nix run .#labels-test-functional reports";
      stage = lib'.pipeline.stages.test;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
    labels-deploy = lib'.pipeline.jobs.nix {
      component = "labels";
      rules = lib'.pipeline.rules.prod ++ [ rules.default ];
      script = "nix run .#labels-deploy";
      stage = lib'.pipeline.stages.deploy;
      tags = [ lib'.pipeline.tags.aarch64 ];
    };
  } // tests;
}
