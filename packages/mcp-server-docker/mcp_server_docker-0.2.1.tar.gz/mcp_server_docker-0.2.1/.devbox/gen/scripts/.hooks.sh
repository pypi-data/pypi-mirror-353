test -z $DEVBOX_COREPACK_ENABLED || corepack enable --install-directory "/Users/christian/mcp/mcp-server-docker/.devbox/virtenv/nodejs/corepack-bin/"
test -z $DEVBOX_COREPACK_ENABLED || export PATH="/Users/christian/mcp/mcp-server-docker/.devbox/virtenv/nodejs/corepack-bin/:$PATH"
echo 'Welcome to devbox!' > /dev/null