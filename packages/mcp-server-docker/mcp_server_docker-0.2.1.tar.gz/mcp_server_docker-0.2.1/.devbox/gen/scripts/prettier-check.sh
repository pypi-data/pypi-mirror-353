set -e

if [ -z "$__DEVBOX_SKIP_INIT_HOOK_f54c6221587e122960156b16029a8b35499ae2666df75a2a85b44a057d494aff" ]; then
    . "/Users/christian/mcp/mcp-server-docker/.devbox/gen/scripts/.hooks.sh"
fi

npx --yes prettier --check *.json *.md
