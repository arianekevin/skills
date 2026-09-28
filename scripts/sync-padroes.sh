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

# Mesma razão, para o que só um par de skills compartilha: fechar-sessao e finalizar-tarefa
# decidem do mesmo jeito se um doc de pendências pertence à tarefa. Fonte: compartilhado/.
for skill in fechar-sessao finalizar-tarefa; do
  cp compartilhado/identificar-doc.md "$skill/skills/$skill/references/identificar-doc.md"
  echo "  → $skill/skills/$skill/references/identificar-doc.md"
done
echo "identificar-doc.md sincronizado."
