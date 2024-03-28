# shell.nix

with import <nixpkgs> { };
let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  name = "tensorflowEnv";
  buildInputs = [
    pythonPackages.python
    pythonPackages.numpy
  ];
}
