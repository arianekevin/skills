#!/usr/bin/env bash
# montar.sh — monta versão principal ou hotfix do nectarcrm e dá push na tag.
#
#   montar.sh principal [--plano]
#   montar.sh hotfix    [--plano] [--base <tag>] <commit>...
#   montar.sh servico   [--plano] <tag-do-crm>
#
# Principal: commit "chore: bump versao" no pom sobre a ponta da origin/alpha, com a tag.
# Hotfix: parte da versão mais recente (principal ou hotfix; com --base vYY.T.NNN, a mais
# recente daquela principal), cria hotfix/<nova> num worktree em .claude/worktrees/,
# aplica só os commits pedidos (cherry-pick -x, na ordem em que entraram na alpha) e põe
# a tag. O hotfix não mexe no pom. --plano mostra o que faria e não cria nada.
# Serviço (rodado no clone do serviço que sobe junto com o CRM): põe a tag do CRM na
# ponta da origin/alpha do serviço, sem bump. O número é sempre o do CRM, mesmo pulando.
#
# Saída: 0 ok · 2 uso/validação · 3 conflito no cherry-pick (nada fica criado).
set -euo pipefail

REPO=${REPO:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}
ALPHA=${ALPHA:-origin/alpha}
POM=${POM:-br.com.colmeia.crm/pom.xml}
ARTIFACT=${ARTIFACT:-nectar-crm}
RE_VERSAO='^v[0-9]{2}\.[1-4]\.[0-9]{3}(\.[0-9]+)?$'
RE_PRINCIPAL='^v[0-9]{2}\.[1-4]\.[0-9]{3}$'

erro() { echo "ERRO: $*" >&2; exit 2; }

cd "$REPO"
git fetch -q origin
# Tag local divergente do origin não derruba a montagem: avisa e segue com a local.
if ! saida=$(git fetch origin --tags 2>&1); then
  echo "AVISO: tags locais diferentes do origin (ficou a local):" >&2
  grep 'rejected' <<<"$saida" | sed 's/^/  /' >&2 || echo "$saida" >&2
fi
git rev-parse -q --verify "$ALPHA^{commit}" >/dev/null || erro "$ALPHA não existe"

versoes() { git tag -l 'v*' | grep -E "$RE_VERSAO" | sort -V; }
existe_tag() { git rev-parse -q --verify "refs/tags/$1" >/dev/null; }

# Período = trimestre da data de hoje (é o que as tags v26.1..v26.4 seguem).
periodo() { echo "v$(date +%y).$(( ($(date +%-m) - 1) / 3 + 1 ))"; }

modo=${1:-}; shift || true
plano=0; base_pedida=""; args=()
while [ $# -gt 0 ]; do
  case $1 in
    --plano) plano=1 ;;
    --base) base_pedida=${2:?--base precisa de uma tag}; shift ;;
    *) args+=("$1") ;;
  esac
  shift
done

case $modo in
principal)
  [ ${#args[@]} -eq 0 ] || erro "a principal sai sempre da ponta da $ALPHA (o bump vai em cima dela)"
  alvo=$(git rev-parse "$ALPHA^{commit}")

  p=$(periodo)
  ultima=$(versoes | grep -E "$RE_PRINCIPAL" | grep -F "$p." | tail -1 || true)
  if [ -n "$ultima" ]; then
    n=$((10#${ultima##*.} + 1))
  else
    n=1
  fi
  nova=$(printf '%s.%03d' "$p" "$n")
  existe_tag "$nova" && erro "tag $nova já existe"

  anterior=$(versoes | grep -E "$RE_PRINCIPAL" | tail -1 || true)
  echo "Versão principal: $nova"
  echo "Sobre:            $(git log -1 --format='%h %cs %s' "$alvo")"
  if [ -n "$anterior" ]; then
    git merge-base --is-ancestor "refs/tags/$anterior" "$alvo" \
      || erro "$ALPHA não contém a versão anterior $anterior"
    echo "Desde $anterior:   $(git rev-list --count "refs/tags/$anterior..$alvo") commits"
  fi
  [ $plano = 1 ] && { echo "(plano: nada criado)"; exit 0; }

  wt="$REPO/.claude/worktrees/versao-$nova"
  [ -e "$wt" ] && erro "worktree já existe: $wt"
  git worktree add -q --detach "$wt" "$alvo"
  versao_pom=${nova#v}
  perl -0pi -e "s{(<artifactId>$ARTIFACT</artifactId>\s*<version>)[^<]+}{\${1}$versao_pom}" "$wt/$POM"
  if git -C "$wt" diff --quiet -- "$POM"; then
    git worktree remove --force "$wt"; erro "não achei a versão do $ARTIFACT no $POM"
  fi
  git -C "$wt" commit -q -m "chore: bump versao para $versao_pom" -- "$POM"
  git -C "$wt" tag "$nova"
  git worktree remove "$wt"

  git push -q origin "refs/tags/$nova"
  echo "Pronto: tag $nova no origin, em $(git log -1 --format='%h %s' "refs/tags/$nova")"
  echo "O bump ainda não está na alpha. Para levar: git push origin refs/tags/$nova:refs/heads/alpha"
  ;;

hotfix)
  [ ${#args[@]} -gt 0 ] || erro "informe os commits do hotfix"

  if [ -n "$base_pedida" ]; then
    principal=$(echo "$base_pedida" | grep -oE '^v[0-9]{2}\.[1-4]\.[0-9]{3}') || erro "--base inválida: $base_pedida"
    existe_tag "$principal" || erro "versão $principal não existe"
  else
    principal=$(versoes | grep -E "$RE_PRINCIPAL" | tail -1)
  fi
  base=$(versoes | grep -E "^${principal//./\\.}(\.[0-9]+)?$" | tail -1)
  ultimo_h=$(echo "$base" | awk -F. 'NF==4 {print $4} NF==3 {print 0}')
  nova="$principal.$((ultimo_h + 1))"
  branch="hotfix/$nova"
  existe_tag "$nova" && erro "tag $nova já existe"
  git show-ref -q --verify "refs/heads/$branch" && erro "branch local $branch já existe"
  git ls-remote --exit-code -q origin "refs/heads/$branch" >/dev/null && erro "branch $branch já existe no origin"

  # Valida e resolve cada commit.
  pedidos=()
  for c in "${args[@]}"; do
    sha=$(git rev-parse -q --verify "$c^{commit}") || erro "commit não encontrado: $c"
    git merge-base --is-ancestor "$sha" "$ALPHA" || erro "$c não está na $ALPHA (hotfix só leva o que já entrou)"
    [ "$(git rev-list --parents -n1 "$sha" | wc -w)" -eq 2 ] || erro "$c é merge; passe os commits dele"
    pedidos+=("$sha")
  done

  # Ordem da alpha; separa o que a base já tem (ancestral dela ou mesmo patch).
  aplicar=(); ja_tem=()
  ordem=$(git rev-list --reverse --topo-order "refs/tags/$base..$ALPHA")
  for sha in $ordem; do
    printf '%s\n' "${pedidos[@]}" | grep -qx "$sha" || continue
    if git cherry "refs/tags/$base" "$sha" "$sha^" | grep -q '^-'; then
      ja_tem+=("$sha")
    else
      aplicar+=("$sha")
    fi
  done
  for sha in "${pedidos[@]}"; do
    grep -qx "$sha" <<<"$ordem" || ja_tem+=("$sha")
  done

  echo "Base:   $base ($(git log -1 --format='%h %cs' "refs/tags/$base"))"
  echo "Nova:   $nova  (branch $branch)"
  echo "Aplica (${#aplicar[@]}):"
  for sha in ${aplicar[@]+"${aplicar[@]}"}; do echo "  $(git log -1 --format='%h %s' "$sha")"; done
  if [ ${#ja_tem[@]} -gt 0 ]; then
    echo "Já na base, pulados (${#ja_tem[@]}):"
    for sha in "${ja_tem[@]}"; do echo "  $(git log -1 --format='%h %s' "$sha")"; done
  fi
  [ ${#aplicar[@]} -gt 0 ] || erro "nada a aplicar: a base já tem todos os commits"
  [ $plano = 1 ] && { echo "(plano: nada criado)"; exit 0; }

  wt="$REPO/.claude/worktrees/$branch"
  [ -e "$wt" ] && erro "worktree já existe: $wt"
  git worktree add -q -b "$branch" "$wt" "refs/tags/$base"

  desfaz() { git -C "$wt" cherry-pick --abort 2>/dev/null || true
             git worktree remove --force "$wt"; git branch -q -D "$branch"; }
  for sha in ${aplicar[@]+"${aplicar[@]}"}; do
    if ! git -C "$wt" cherry-pick -x "$sha" >/dev/null 2>&1; then
      arquivos=$(git -C "$wt" diff --name-only --diff-filter=U)
      echo "CONFLITO em $(git log -1 --format='%h %s' "$sha")" >&2
      echo "Arquivos:" >&2; sed 's/^/  /' <<<"$arquivos" >&2
      echo "Commits da alpha que mexem nesses arquivos e a base não tem (candidatos a dependência):" >&2
      # shellcheck disable=SC2086
      git log --format='  %h %cs %s' "refs/tags/$base..$sha^" -- $arquivos >&2 || true
      desfaz
      echo "Nada criado." >&2
      exit 3
    fi
  done

  git -C "$wt" tag "$nova"

  git push -q origin "refs/heads/$branch" "refs/tags/$nova"
  echo "Pronto: branch $branch e tag $nova no origin (worktree $wt)"
  ;;

servico)
  [ ${#args[@]} -eq 1 ] || erro "informe a tag do CRM (ex.: v26.4.007)"
  nova=${args[0]}
  grep -qE "$RE_VERSAO" <<<"$nova" || erro "tag inválida: $nova"
  grep -qE "$RE_PRINCIPAL" <<<"$nova" || erro "$nova é hotfix; serviço só acompanha a versão principal"
  existe_tag "$nova" && erro "tag $nova já existe"
  alvo=$(git rev-parse "$ALPHA^{commit}")

  anterior=$(versoes | grep -E "$RE_PRINCIPAL" | tail -1 || true)
  echo "Serviço:          $(basename "$REPO")"
  echo "Tag (do CRM):     $nova"
  echo "Sobre:            $(git log -1 --format='%h %cs %s' "$alvo")"
  if [ -n "$anterior" ]; then
    [ "$(printf '%s\n%s\n' "$anterior" "$nova" | sort -V | tail -1)" = "$nova" ] \
      || erro "$nova é anterior à última do serviço ($anterior)"
    git merge-base --is-ancestor "refs/tags/$anterior" "$alvo" \
      || erro "$ALPHA não contém a versão anterior $anterior"
    echo "Desde $anterior:   $(git rev-list --count "refs/tags/$anterior..$alvo") commits"
  fi
  [ $plano = 1 ] && { echo "(plano: nada criado)"; exit 0; }

  git tag "$nova" "$alvo"
  git push -q origin "refs/tags/$nova"
  echo "Pronto: tag $nova no origin, em $(git log -1 --format='%h %s' "refs/tags/$nova")"
  ;;

*)
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
  ;;
esac
