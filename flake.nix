{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = inputs@{ self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };
      lib = pkgs.lib;
    in {
      packages.${system} = {
        signal-export = import ./default.nix pkgs;
      };
      apps.${system} = {
        sigexport = {
          type = "app";
          program = "${self.packages.x86_64-linux.signal-export}/bin/sigexport";
        };
      };
  };
}
