#!/bin/bash
set -e

BACKUP_DIR="/backups"
VAULT_DIR="/vault"

echo "[torus-backup] Starting backup daemon"

while true; do
    DATE=$(date +%Y-%m-%d_%H-%M-%S)
    ARCHIVE="$BACKUP_DIR/torus_vault_$DATE.tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -d "$VAULT_DIR" ] && [ "$(ls -A $VAULT_DIR 2>/dev/null)" ]; then
        tar -czf "$ARCHIVE" \
          --exclude='node_modules' \
          --exclude='.git' \
          --exclude='.obsidian/workspace.json' \
          -C "$VAULT_DIR" . 2>/dev/null || true
        echo "[torus-backup] $(date): Archive created: $ARCHIVE ($(du -h $ARCHIVE | cut -f1))"
    else
        echo "[torus-backup] $(date): WARNING: Vault not mounted at $VAULT_DIR"
    fi
    
    # Keep only last 7 backups
    ls -t "$BACKUP_DIR"/torus_vault_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm -f
    
    # Sleep 1 hour
    sleep 3600
done
