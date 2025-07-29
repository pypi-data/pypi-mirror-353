{ lib', pkgs, self' }: {
  default = pkgs.mkShell {
    packages = pkgs.lib.flatten [
      lib'.envs.labels.dependencies.editable
      lib'.envs.labels.envars
      (pkgs.lib.attrValues self'.packages)
    ];
    env = {
      UV_NO_SYNC = "1";
      UV_PYTHON = "${lib'.envs.labels.venv.editable}/bin/python";
      UV_PYTHON_DOWNLOADS = "never";
    };
    shellHook = ''
      unset PYTHONPATH
      source labels-envars
    '';
  };
}
