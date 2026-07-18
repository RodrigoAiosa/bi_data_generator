# EscolaDAX

Este repositório contém **dois projetos** independentes de geração de dados
fictícios em modelo estrela (fato + dimensões), para praticar Power BI, DAX
e modelagem dimensional. Cada um vive na sua própria pasta, com seu próprio
`app.py` e `requirements.txt`.

## 📁 `escoladax_simples/`
Versão enxuta, com **8 setores de negócio** (Varejo, Financeiro, Saúde,
E-commerce, Logística, Educação, Imobiliário e SaaS B2B).

Rodar localmente:
```bash
cd escoladax_simples
pip install -r requirements.txt
streamlit run app.py
```

## 📁 `bi_data_generator/`
Versão completa, com **55 setores de negócio**, geração de medidas DAX
automática para qualquer setor, dicionário de dados, suporte a PT/EN e
dashboard interativo.

Rodar localmente:
```bash
cd bi_data_generator
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit Cloud

Como os dois apps ficam em subpastas, ao criar o app no Streamlit Cloud
aponte o **"Main file path"** para o `app.py` da pasta desejada, por exemplo:

- `escoladax_simples/app.py`
- `bi_data_generator/app.py`

Cada app usa o `requirements.txt` da sua própria pasta.
