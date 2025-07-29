{
   description = "A devbox shell";

   inputs = {
     nixpkgs.url = "github:NixOS/nixpkgs/3a05eebede89661660945da1f151959900903b6a?narHash=sha256-Ly2fBL1LscV%2BKyCqPRufUBuiw%2BzmWrlJzpWOWbahplg%3D";
   };

   outputs = {
     self,
     nixpkgs,
   }:
      let
        pkgs = nixpkgs.legacyPackages.aarch64-darwin;
      in
      {
        devShells.aarch64-darwin.default = pkgs.mkShell {
          buildInputs = [
            (builtins.trace "downloading nodejs@latest" (builtins.fetchClosure {
              
              fromStore = "https://cache.nixos.org";
              fromPath = "/nix/store/2ibv0dpai0wwhwlhcy04y0hllqilawhq-nodejs-23.2.0";
              inputAddressed = true;
            }))
            (builtins.trace "downloading uv@latest" (builtins.fetchClosure {
              
              fromStore = "https://cache.nixos.org";
              fromPath = "/nix/store/yvdr8x3lfq0m669l7vznyjg51259vzl4-uv-0.4.30";
              inputAddressed = true;
            }))
            (builtins.trace "downloading taplo@latest" (builtins.fetchClosure {
              
              fromStore = "https://cache.nixos.org";
              fromPath = "/nix/store/nzb1qgckvmdq9algzjcagb4yvckhdzhn-taplo-0.9.3";
              inputAddressed = true;
            }))
          ];
        };
      };
 }
