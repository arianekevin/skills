# O relatório da manhã

Quem lê acabou de acordar. O relatório serve a duas coisas: **saber o que mudou** e **responder o que
ficou para ele**. Vai no doc de pendências (seção `## Modo noturno <AAAA-MM-DD>`) e no chat.

## Regras

- **A primeira linha é o veredito, em números.** Nada de "a noite foi produtiva".
- **Perguntas primeiro.** É o que destrava o resto; o feito ele lê depois.
- **Cada pergunta se basta sozinha:** quem lê não lembra do contexto da noite.
- **Saída colada, não parafraseada**, para o que travou ou foi revertido.
- **Sem enfeite e sem desculpa.**

## Formato

```markdown
## Modo noturno 2026-10-27

**7 itens · 4 feitos · 2 congelados (1 com branch à parte) · 1 travado**

### Perguntas para você

1. **Exportação: PDF no servidor ou no navegador?**
   O item 5 precisa gerar o PDF da peça. Gerar no servidor pede uma dependência nova (`weasyprint`).
   - **Servidor (recomendo)** — mesmo resultado em qualquer navegador; implementado em
     `noturno/2026-10-27-pdf-servidor`, testes verdes. Aprovar = trazer a branch.
   - Navegador — sem dependência nova, mas a quebra de página varia por navegador.

2. **Apagar as 3 tabelas antigas de importação?**
   Ninguém lê delas desde o commit `a1b2c3d`. Destrutivo: não fiz nada.
   - Apagar numa migration nova
   - Manter por mais uma versão (recomendo) — custo zero, e dá tempo de confirmar em produção

### Feito

| Item | Commit | Pronto quando |
|---|---|---|
| Importador com teste | `e4f5g6h` | `pytest tests/importador` → 12 passed |
| ... | | |

### Decidi sozinha

- **Mensagem de erro do importador em português**, como o resto da API. Desfazer: `e4f5g6h`, 1 arquivo.
- ...

### Travado

- **Item 7 — sincronizar com o storage:** o bucket de homologação recusou a credencial local.

      AccessDenied: User is not authorized to perform s3:PutObject

  Falta: credencial com escrita no bucket de homologação.

### Achados fora do combinado

- O endpoint de busca não pagina — apareceu no item 3. Não mexi.
```

Nada a declarar numa seção: omita a seção, não escreva "nenhum".
