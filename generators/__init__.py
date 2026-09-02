"""
generators/__init__.py

Propositalmente vazio: os 213 módulos de setor NÃO são importados aqui.
Antes, este arquivo importava as 213 funções gerar_<setor> de uma vez
(e cada módulo instanciava seu próprio Faker no import), o que rodava
por completo sempre que qualquer código tocava o pacote `generators`
(ex.: `from generators.helpers import to_zip`) — mesmo quando só 1 dos
200 setores seria usado na sessão. Isso dominava o tempo de cold start.

O carregamento de cada setor agora é sob demanda, via `config.obter_gerador`,
que importa e cacheia só o módulo `generators.<setor>` escolhido pelo usuário.
"""
