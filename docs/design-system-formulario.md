# Design system — formulário de acesso (gate)

Tokens em `public/estilo.css` (`:root`) e componentes sob `.gate`.

| Token | Valor | Uso |
|---|---|---|
| `--sp-1…6` | .25 / .5 / .75 / 1 / 1.5 / 2 rem | todo espaçamento (escala de 4 px) |
| `--raio-s/m/g` | 6 / 8 / 14 px | tags, campos e botões, cartão |
| `--alvo` | 48 px | altura mínima de campos, botões e abas (mín. absoluto 44 px) |
| `--foco` | 2 px amarelo | anel de foco visível em todo controle |
| `--ac` `--ok` `--erro` | #F2C811 / #3ecf8e / #ff6b6b | ação, sucesso, erro |
| `--txt-s` / `--txt-m` | .85 / 1 rem | rótulos e dicas / texto base (campos em 16 px) |

## Componentes
- **Campo** (`label > .rot + input/select + .dica`): rótulo acima, asterisco vermelho nos obrigatórios, dica abaixo (`aria-live`). Estados: padrão, hover, foco, `.valido` (verde), `.invalido` (vermelho + mensagem), `:disabled`.
- **Grupo** (`fieldset.grupo > legend`): agrupa campos relacionados (Seus dados / Seu perfil).
- **Botão** (`.btn.primario.grande`): 48 px, estados hover/active/disabled ("Cadastrando…").
- **Abas** (`role=tablist`): setas ← → Home End, `aria-selected`, painéis `role=tabpanel`.
- **Chips**, **dica com ação** (`.link-dica`, ex.: "Você quis dizer …?"), **rodapé** (`.gate-rodape`).

## Regras de comportamento
- Validação ao sair do campo; erros mostrados em texto (não só cor); envio inválido foca o primeiro erro.
- O sistema absorve esforço: máscara de celular, e-mail em minúsculas e sem espaços, sugestão de correção de domínio, Estado sugerido pelo DDD (editável), lista de cidades pré-carregada.
- Respeita `prefers-reduced-motion`.
