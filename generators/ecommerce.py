import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .helpers import new_ids, dcalendario, rand_dates

def gerar_ecommerce(n_linhas: int, start_date: str, end_date: str) -> dict[str, pd.DataFrame]:
    """
    Gera dados do setor de E-commerce (Star Schema)
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # ========== DIMENSÕES ==========
    
    # DimCliente (500-3000 clientes)
    n_clientes = min(3000, max(500, n_linhas // 10))
    cliente_ids = new_ids(n_clientes, "CLI")
    
    sexos = ["M", "F", "Prefiro não informar"]
    ufs = ["SP", "RJ", "MG", "RS", "BA", "PR", "PE", "CE", "SC", "GO"]
    
    dim_cliente = pd.DataFrame({
        "sk_cliente": cliente_ids,
        "id_cliente": cliente_ids,
        "nome": [f"Cliente {i+1}" for i in range(n_clientes)],
        "email": [f"cliente{i+1}@email.com" for i in range(n_clientes)],
        "sexo": np.random.choice(sexos, n_clientes, p=[0.48, 0.48, 0.04]),
        "idade": np.random.randint(18, 80, n_clientes),
        "uf": np.random.choice(ufs, n_clientes),
        "cidade": [f"Cidade {np.random.randint(1,50)}" for _ in range(n_clientes)],
        "data_cadastro": rand_dates(start - timedelta(days=730), start, n_clientes),
        "score_fidelidade": np.random.randint(0, 100, n_clientes)
    })
    
    # DimProduto (200-1000 produtos)
    n_produtos = min(1000, max(200, n_linhas // 20))
    produto_ids = new_ids(n_produtos, "PRO")
    
    categorias = ["Eletrônicos", "Moda", "Casa e Decoração", "Beleza", "Esportes", 
                  "Livros", "Brinquedos", "Alimentos", "Ferramentas", "Informática"]
    
    dim_produto = pd.DataFrame({
        "sk_produto": produto_ids,
        "id_produto": produto_ids,
        "nome_produto": [f"Produto {i+1}" for i in range(n_produtos)],
        "categoria": np.random.choice(categorias, n_produtos),
        "preco_unitario": np.random.uniform(10, 2000, n_produtos).round(2),
        "custo_unitario": np.random.uniform(5, 1000, n_produtos).round(2),
        "peso_kg": np.random.uniform(0.1, 10, n_produtos).round(2),
        "marca": [f"Marca {np.random.randint(1,30)}" for _ in range(n_produtos)]
    })
    
    # DimPlataforma
    plataformas = ["Website", "App iOS", "App Android", "WhatsApp", "Marketplace"]
    
    dim_plataforma = pd.DataFrame({
        "sk_plataforma": new_ids(len(plataformas), "PLA"),
        "nome_plataforma": plataformas,
        "taxa_comissao": [0.0, 0.0, 0.0, 0.0, 0.12]
    })
    
    # DimPagamento
    metodos = ["Cartão Crédito", "Cartão Débito", "PIX", "Boleto", "PayPal", "Mercado Pago"]
    parcelamentos = [1, 2, 3, 4, 5, 6, 8, 10, 12]
    
    dim_pagamento = pd.DataFrame({
        "sk_pagamento": new_ids(len(metodos), "PAG"),
        "metodo": metodos,
        "max_parcelas": np.random.choice([1, 3, 6, 12], len(metodos)),
        "taxa_juros": np.random.uniform(0, 0.05, len(metodos)).round(3)
    })
    
    # DimFrete
    transportadoras = ["Correios", "Jadlog", "Loggi", "Total Express", "DHL", "FedEx"]
    
    dim_frete = pd.DataFrame({
        "sk_frete": new_ids(len(transportadoras), "FRE"),
        "transportadora": transportadoras,
        "prazo_medio_dias": np.random.randint(2, 15, len(transportadoras)),
        "valor_kg": np.random.uniform(2, 15, len(transportadoras)).round(2)
    })
    
    # ========== TABELA FATO ==========
    # Gerar pedidos
    datas_pedido = rand_dates(start, end, n_linhas)
    
    # Selecionar chaves estrangeiras
    cliente_keys = np.random.choice(dim_cliente["sk_cliente"], n_linhas)
    produto_keys = np.random.choice(dim_produto["sk_produto"], n_linhas)
    plataforma_keys = np.random.choice(dim_plataforma["sk_plataforma"], n_linhas)
    pagamento_keys = np.random.choice(dim_pagamento["sk_pagamento"], n_linhas)
    frete_keys = np.random.choice(dim_frete["sk_frete"], n_linhas)
    
    # Calcular valores
    precos = dim_produto.set_index("sk_produto")["preco_unitario"].to_dict()
    custos = dim_produto.set_index("sk_produto")["custo_unitario"].to_dict()
    pesos = dim_produto.set_index("sk_produto")["peso_kg"].to_dict()
    
    quantidade = np.random.randint(1, 6, n_linhas)
    valor_produtos = [precos[pk] * q for pk, q in zip(produto_keys, quantidade)]
    custo_produtos = [custos[pk] * q for pk, q in zip(produto_keys, quantidade)]
    
    # Calcular frete (baseado no peso)
    valor_frete = [pesos[pk] * q * np.random.uniform(3, 8) for pk, q in zip(produto_keys, quantidade)]
    
    # Desconto (0-30%)
    desconto_percent = np.random.uniform(0, 0.3, n_linhas)
    desconto_valor = valor_produtos * desconto_percent
    
    valor_total = valor_produtos + valor_frete - desconto_valor
    
    # Status do pedido
    status = np.random.choice(
        ["Entregue", "Processando", "Cancelado", "Devolvido", "Extraviado"],
        n_linhas,
        p=[0.75, 0.15, 0.05, 0.03, 0.02]
    )
    
    # Avaliação (1-5, apenas entregues)
    avaliacao = [np.random.randint(1, 6) if s == "Entregue" and np.random.random() < 0.6 else None 
                 for s in status]
    
    fato_pedido = pd.DataFrame({
        "sk_pedido": new_ids(n_linhas, "PED"),
        "data_pedido": datas_pedido,
        "data_entrega": [d + timedelta(days=np.random.randint(2, 15)) if s == "Entregue" else None 
                         for d, s in zip(datas_pedido, status)],
        "quantidade": quantidade,
        "valor_produtos": valor_produtos,
        "valor_frete": valor_frete,
        "desconto": desconto_valor,
        "valor_total": valor_total,
        "status": status,
        "avaliacao": avaliacao,
        "sk_cliente": cliente_keys,
        "sk_produto": produto_keys,
        "sk_plataforma": plataforma_keys,
        "sk_pagamento": pagamento_keys,
        "sk_frete": frete_keys
    })
    
    return {
        "FatoPedido": fato_pedido,
        "DimCliente": dim_cliente,
        "DimProduto": dim_produto,
        "DimPlataforma": dim_plataforma,
        "DimPagamento": dim_pagamento,
        "DimFrete": dim_frete,
        "dCalendario": dcalendario(start, end)
    }
