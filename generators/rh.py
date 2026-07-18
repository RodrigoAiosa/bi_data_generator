import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_rh(n_linhas: int, start_date, end_date) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Recursos Humanos (Star Schema)
    
    Tabelas geradas:
    - FatoHorasTrabalhadas: Registros diários de horas trabalhadas
    - DimFuncionario: Funcionários da empresa
    - DimDepartamento: Departamentos da empresa
    - DimCargo: Cargos e salários
    - DimProjeto: Projetos da empresa
    - DimAvaliacao: Avaliações de desempenho
    - dCalendario: Tabela calendário
    """
    # Converte para datetime se necessário
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = start_date
    
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = end_date
    
    # ========== DIMENSÕES ==========
    
    # DimFuncionario (200-1000 funcionários)
    n_funcionarios = min(1000, max(200, n_linhas // 15))
    funcionario_ids = new_ids(n_funcionarios, "FUN")
    
    # Geração de dados demográficos
    estados = ["SP", "RJ", "MG", "RS", "BA", "PR", "PE", "CE", "SC", "GO"]
    escolaridades = ["Ensino Médio", "Graduação", "Pós-graduação", "Mestrado", "Doutorado"]
    
    dim_funcionario = pd.DataFrame({
        "sk_funcionario": funcionario_ids,
        "id_funcionario": funcionario_ids,
        "nome": [f"Funcionário {i+1}" for i in range(n_funcionarios)],
        "cpf": [f"{np.random.randint(100,999)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}-{np.random.randint(10,99)}" 
                for _ in range(n_funcionarios)],
        "data_nascimento": rand_dates(start - timedelta(days=365*40), start - timedelta(days=365*18), n_funcionarios),
        "sexo": np.random.choice(["M", "F"], n_funcionarios, p=[0.52, 0.48]),
        "estado": np.random.choice(estados, n_funcionarios),
        "escolaridade": np.random.choice(escolaridades, n_funcionarios, p=[0.2, 0.45, 0.2, 0.1, 0.05]),
        "data_admissao": rand_dates(start - timedelta(days=1825), start, n_funcionarios),
        "data_demissao": [None if np.random.random() > 0.15 else rand_dates(start, end, 1)[0] 
                          for _ in range(n_funcionarios)],
        "ativo": np.random.choice([True, False], n_funcionarios, p=[0.85, 0.15])
    })
    
    # DimDepartamento
    departamentos = ["Vendas", "Marketing", "TI", "RH", "Financeiro", "Operações", "Logística", "Jurídico", "Pesquisa", "Qualidade"]
    
    dim_departamento = pd.DataFrame({
        "sk_departamento": new_ids(len(departamentos), "DEP"),
        "nome_departamento": departamentos,
        "centro_custo": [f"CC{np.random.randint(1000,9999)}" for _ in departamentos],
        "gerente_responsavel": [f"Gerente {chr(65+i)}" for i in range(len(departamentos))],
        "orcamento_anual": np.random.uniform(500000, 5000000, len(departamentos)).round(2)
    })
    
    # DimCargo
    cargos = ["Analista Jr", "Analista Pl", "Analista Sr", "Coordenador", "Gerente", "Diretor", "Estagiário", "Assistente", "Especialista", "Consultor"]
    niveis = ["Júnior", "Pleno", "Sênior", "Liderança", "Executivo", "Estágio", "Operacional", "Tático", "Estratégico", "Consultivo"]
    salarios_base = [3500, 5500, 8500, 12000, 18000, 30000, 2000, 3000, 10000, 15000]
    
    dim_cargo = pd.DataFrame({
        "sk_cargo": new_ids(len(cargos), "CAR"),
        "nome_cargo": cargos,
        "nivel": niveis,
        "salario_base": salarios_base,
        "beneficios": np.random.choice(["VR+VT", "VR+VT+Plano", "VR+VT+Plano+Bônus", "Completo", "Básico"], len(cargos)),
        "carga_horaria_semanal": np.random.choice([30, 36, 40, 44], len(cargos))
    })
    
    # DimProjeto (50-200 projetos)
    n_projetos = min(200, max(50, n_linhas // 50))
    projeto_ids = new_ids(n_projetos, "PROJ")
    
    status_projeto = ["Em andamento", "Concluído", "Cancelado", "Planejado", "Pausado"]
    
    dim_projeto = pd.DataFrame({
        "sk_projeto": projeto_ids,
        "id_projeto": projeto_ids,
        "nome_projeto": [f"Projeto {i+1}" for i in range(n_projetos)],
        "status_projeto": np.random.choice(status_projeto, n_projetos, p=[0.4, 0.35, 0.1, 0.1, 0.05]),
        "data_inicio": rand_dates(start - timedelta(days=365), start + timedelta(days=180), n_projetos),
        "data_fim_prevista": [di + timedelta(days=np.random.randint(30, 365)) for di in rand_dates(start, end, n_projetos)],
        "orcamento": np.random.uniform(50000, 500000, n_projetos).round(2),
        "categoria": np.random.choice(["TI", "Negócios", "Marketing", "Infraestrutura", "P&D"], n_projetos)
    })
    
    # DimAvaliacao
    avaliacoes = ["Excelente", "Bom", "Regular", "Necessita Melhoria", "Insatisfatório"]
    
    dim_avaliacao = pd.DataFrame({
        "sk_avaliacao": new_ids(len(avaliacoes), "AVA"),
        "nota": [5, 4, 3, 2, 1],
        "descricao": avaliacoes,
        "bonus_percentual": [0.20, 0.10, 0.05, 0.0, 0.0]
    })
    
    # ========== TABELA FATO ==========
    # Gerar registros de horas trabalhadas por projeto
    
    datas_registro = rand_dates(start, end, n_linhas)
    
    # Selecionar chaves estrangeiras (apenas funcionários ativos)
    funcionarios_ativos = dim_funcionario[dim_funcionario["ativo"] == True]["sk_funcionario"].tolist()
    if not funcionarios_ativos:
        funcionarios_ativos = dim_funcionario["sk_funcionario"].tolist()
    
    funcionario_keys = np.random.choice(funcionarios_ativos, n_linhas)
    departamento_keys = np.random.choice(dim_departamento["sk_departamento"], n_linhas)
    cargo_keys = np.random.choice(dim_cargo["sk_cargo"], n_linhas)
    projeto_keys = np.random.choice(dim_projeto["sk_projeto"], n_linhas)
    avaliacao_keys = np.random.choice(dim_avaliacao["sk_avaliacao"], n_linhas, p=[0.2, 0.35, 0.25, 0.15, 0.05])
    
    # Horas trabalhadas (4-12 horas por dia)
    horas_trabalhadas = np.random.randint(4, 13, n_linhas)
    
    # Horas extras (0-4 horas)
    horas_extras = np.random.choice([0, 1, 2, 3, 4], n_linhas, p=[0.55, 0.15, 0.12, 0.1, 0.08])
    
    # Produtividade (0-100%)
    produtividade = np.random.uniform(0.5, 1.0, n_linhas).round(2)
    
    # Satisfação (1-5)
    satisfacao = np.random.randint(1, 6, n_linhas)
    
    # Cálculo de custo (baseado no salário/hora)
    # Buscar salário base do cargo
    salarios_dict = dim_cargo.set_index("sk_cargo")["salario_base"].to_dict()
    salario_hora = [salarios_dict.get(ck, 5000) / 160 for ck in cargo_keys]  # 160 horas/mês
    
    custo_total = [(sh * (ht + he)) for sh, ht, he in zip(salario_hora, horas_trabalhadas, horas_extras)]
    
    # Faltas (0 ou 1)
    falta = np.random.choice([0, 1], n_linhas, p=[0.92, 0.08])
    
    # Horas extras aprovadas
    horas_extras_aprovadas = [he if np.random.random() > 0.2 else 0 for he in horas_extras]
    
    fato_horas = pd.DataFrame({
        "sk_registro": new_ids(n_linhas, "REG"),
        "data_registro": datas_registro,
        "ano": [d.year for d in datas_registro],
        "mes": [d.month for d in datas_registro],
        "horas_trabalhadas": horas_trabalhadas,
        "horas_extras": horas_extras,
        "horas_extras_aprovadas": horas_extras_aprovadas,
        "produtividade": produtividade,
        "satisfacao": satisfacao,
        "custo_diario": [round(c, 2) for c in custo_total],
        "falta": falta,
        "sk_funcionario": funcionario_keys,
        "sk_departamento": departamento_keys,
        "sk_cargo": cargo_keys,
        "sk_projeto": projeto_keys,
        "sk_avaliacao": avaliacao_keys
    })
    
    return {
        "FatoHorasTrabalhadas": fato_horas,
        "DimFuncionario": dim_funcionario,
        "DimDepartamento": dim_departamento,
        "DimCargo": dim_cargo,
        "DimProjeto": dim_projeto,
        "DimAvaliacao": dim_avaliacao,
        "dCalendario": dcalendario(start, end)
    }
