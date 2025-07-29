{ makeSearchPaths, makeScript, outputs, __system__, ... }: {
  dev = {
    labels = {
      source = [
        outputs."/labels/env"
        (makeSearchPaths { pythonPackage = [ "$PWD/labels" ]; })
      ];
    };
  };
  imports = [ ./env/tree_sitter_patch/makes.nix ./env/makes.nix ];
  secretsForEnvFromSops = {
    labels = {
      vars = [ "CACHE_URL" "CACHE_USER_WRITE_PASSWORD" ];
      manifest = "/skims/secrets/dev.yaml";
    };
  };
  secretsForAwsFromGitlab = {
    prodLabels = {
      roleArn = "arn:aws:iam::205810638802:role/prod_labels";
      duration = 3600;
    };
  };
  inputs = {
    # Also used by skims
    TreeSitterGemFileLockTarball = builtins.fetchTarball {
      url =
        "https://github.com/fluidattacks/tree-sitter-gemfilelock/archive/a0c57ba1edbe39ec0327838995d104aab2ed16c3.tar.gz";
      sha256 = "sha256-MBMJX9mi2fj6wfZqYw5VwHhbRZakSRBuqQ4wsIhUnlQ=";
    };
    TreeSitterMixLockTarball = builtins.fetchTarball {
      url =
        "https://github.com/fluidattacks/tree-sitter-mix_lock/archive/8ef8b09bf9b11369ce1d83478af3971e6dfe21b9.tar.gz";
      sha256 = "sha256:1fxj1s6p18qqfb876yxzcy0n3rmp6hipxym3hjnacbaa0a42s0p5";
    };
  };
  jobs."/labels" = makeScript {
    name = "labels";
    entrypoint = ''
      labels "$@"
    '';
    searchPaths = { source = [ outputs."/labels/env" ]; };
  };
}
