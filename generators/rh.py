import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_rh(n_linhas: int, start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de Recursos Humanos (Star Schema)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # ========== DIMENSÕES ==========
    
    # DimFuncionario (200-1000 funcionários)
    n_funcionarios = min(1000, max(200, n_linhas // 15))
    funcionario_ids = new_ids(n_funcionarios, "FUN")
    
    dim_funcionario = pd.DataFrame({
        "sk_funcionario": funcionario_ids,
        "id_funcionario": funcionario_ids,
        "nome": [f"Funcionário {i+1}" for i in range(n_funcionarios)],
        "cpf": [f"{np.random.randint(100,999)}.{np.random.randint(100,999)}.{np.random.randint(100,999)}-{np.random.randint(10,99)}" 
                for _ in range(n_funcionarios)],
        "data_nascimento": rand_dates(start - timedelta(days=365*40), start - timedelta(days=365*18), n_funcionarios),
        "sexo": np.random.choice(["M", "F"], n_funcionarios, p=[0.52, 0.48]),
        "escolaridade": np.random.choice(["Ensino Médio", "Graduação", "Pós-graduação", "Mestrado", "Doutorado"], 
                                         n_funcionarios, p=[0.2, 0.45, 0.2, 0.1, 0.05]),
        "data_admissao": rand_dates(start - timedelta(days=1825), start, n_funcionarios)
    })
    
    # DimDepartamento
    departamentos = ["Vendas", "Marketing", "TI", "RH", "Financeiro", "Operações", "Logística", "Jurídico"]
    
    dim_departamento = pd.DataFrame({
        "sk_departamento": new_ids(len(departamentos), "DEP"),
        "nome_departamento": departamentos,
        "centro_custo": [f"CC{np.random.randint(1000,9999)}" for _ in departamentos],
        "gerente_responsavel": [f"Gerente {chr(65+i)}" for i in range(len(departamentos))]
    })
    
    # DimCargo
    cargos = ["Analista Jr", "Analista Pl", "Analista Sr", "Coordenador", "Gerente", "Diretor", "Estagiário"]
    niveis = ["Júnior", "Pleno", "Sênior", "Liderança", "Executivo", "Estágio"]
    salarios_base = [3500, 5500, 8500, 12000, 18000, 30000, 2000]
    
    dim_cargo = pd.DataFrame({
        "sk_cargo": new_ids(len(cargos), "CAR"),
        "nome_cargo": cargos,
        "nivel": niveis,
        "salario_base": salarios_base,
        "beneficios": np.random.choice(["VR+VT", "VR+VT+Plano", "VR+VT+Plano+Bônus", "Completo"], len(cargos))
    })
    
    # DimProjeto (50-200 projetos)
    n_projetos = min(200, max(50, n_linhas // 50))
    projeto_ids = new_ids(n_projetos, "PROJ")
    
    dim_projeto = pd.DataFrame({
        "sk_projeto": projeto_ids,
        "id_projeto": projeto_ids,
        "nome_projeto": [f"Projeto {i+1}" for i in range(n_projetos)],
        "status_projeto": np.random.choice(["Em andamento", "Concluído", "Cancelado", "Planejado"], n_projetos),
        "orcamento": np.random.uniform(50000, 500000, n_projetos).round(2)
    })
    
    # DimAvaliacao
    avaliacoes = ["Excelente", "Bom", "Regular", "Necessita Melhoria", "Insatisfatório"]
    
    dim_avaliacao = pd.DataFrame({
        "sk_avaliacao": new_ids(len(avaliacoes), "AVA"),
        "nota": [5, 4, 3, 2, 1],
        "descricao": avaliacoes
    })
    
    # ========== TABELA FATO ==========
    # Gerar registros de horas trabalhadas por projeto
    
    datas_registro = rand_dates(start, end, n_linhas)
    
    # Selecionar chaves estrangeiras
    funcionario_keys = np.random.choice(dim_funcionario["sk_funcionario"], n_linhas)
    departamento_keys = np.random.choice(dim_departamento["sk_departamento"], n_linhas)
    cargo_keys = np.random.choice(dim_cargo["sk_cargo"], n_linhas)
    projeto_keys = np.random.choice(dim_projeto["sk_projeto"], n_linhas)
    avaliacao_keys = np.random.choice(dim_avaliacao["sk_avaliacao"], n_linhas, p=[0.2, 0.35, 0.25, 0.15, 0.05])
    
    # Horas trabalhadas (4-12 horas por dia)
    horas_trabalhadas = np.random.randint(4, 13, n_linhas)
    
    # Horas extras (0-4 horas)
    horas_extras = np.random.choice([0, 1, 2, 3, 4], n_linhas, p=[0.6, 0.15, 0.1, 0.08, 0.07])
    
    # Produtividade (0-100%)
    produtividade = np.random.uniform(0.5, 1.0, n_linhas).round(2)
    
    # Satisfação (1-5)
    satisfacao = np.random.randint(1, 6, n_linhas)
    
    # Cálculo de custo (baseado no salário/hora)
    salarios = dim_cargo.set_index("sk_cargo")["salario_base"].to_dict()
    salario_hora = [salarios[ck] / 160 for ck in cargo_keys]  # 160 horas/mês
    custo_total = salario_hora * (horas_trabalhadas + horas_extras)
    
    fato_horas = pd.DataFrame({
        "sk_registro": new_ids(n_linhas, "REG"),
        "data_registro": datas_registro,
        "horas_trabalhadas": horas_trabalhadas,
        "horas_extras": horas_extras,
        "produtividade": produtividade,
        "satisfacao": satisfacao,
        "custo_diario": custo_total,
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
