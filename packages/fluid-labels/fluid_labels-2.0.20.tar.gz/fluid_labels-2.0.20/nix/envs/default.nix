{ inputs, pkgs, projectPath }: {
  labels = pkgs.callPackage ./labels { inherit projectPath inputs; };
}
