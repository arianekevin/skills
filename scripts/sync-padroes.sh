#!/usr/bin/env bash
# Copia PADROES.md (fonte única, na raiz) para dentro de cada plugin.
# Necessário porque cada plugin é instalado isoladamente — um arquivo só na raiz
# do repositório não acompanha a instalação e a skill não o enxerga em runtime.
set -euo pipefail
cd "$(dirname "$0")/.."
for skill in */skills/*/; do
  cp PADROES.md "$skill/PADROES.md"
  echo "  → $skill"
done
echo "PADROES.md sincronizado."
