# BI Data Generator

## 📋 Sobre o Projeto

O **BI Data Generator** é uma ferramenta potente para gerar dados estruturados e realistas, otimizados para análise em plataformas de Business Intelligence (BI) como Power BI, Tableau e ferramentas similares.

## 🎯 Funcionalidades

- ✅ Geração de dados realistas e estruturados
- ✅ Suporte a múltiplos formatos (CSV, JSON, Parquet, etc.)
- ✅ Configuração flexível e customizável
- ✅ Relações entre tabelas mantidas
- ✅ Escalável para grandes volumes de dados
- ✅ Performance otimizada

## 🚀 Quickstart

### Pré-requisitos

- Python 3.8+
- pip
- Git

### Instalação

```bash
# Clone o repositório
git clone https://github.com/RodrigoAiosa/bi_data_generator.git
cd bi_data_generator

# Instale as dependências
pip install -r requirements.txt
```

### Uso Básico

```python
from bi_data_generator import DataGenerator

# Inicialize o gerador
generator = DataGenerator(
    rows=10000,
    schema_file='schema.json',
    output_format='csv'
)

# Gere os dados
generator.generate()

# Salve o arquivo
generator.save('output/data.csv')
```

## 📁 Estrutura do Projeto

```
bi_data_generator/
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   ├── __init__.py
│   ├── generator.py
│   ├── schema.py
│   └── utils/
│       └── formatters.py
├── examples/
│   ├── basic_example.py
│   ├── schema_example.json
│   └── advanced_usage.py
├── tests/
│   ├── test_generator.py
│   └── test_schema.py
└── docs/
    ├── installation.md
    ├── usage.md
    └── api.md
```

## 🔧 Configuração

### Arquivo de Schema

Crie um arquivo `schema.json` para definir a estrutura dos dados:

```json
{
  "tables": [
    {
      "name": "customers",
      "rows": 5000,
      "columns": [
        {
          "name": "customer_id",
          "type": "integer",
          "unique": true
        },
        {
          "name": "customer_name",
          "type": "string",
          "faker": "name"
        },
        {
          "name": "email",
          "type": "string",
          "faker": "email"
        },
        {
          "name": "created_date",
          "type": "date",
          "min": "2020-01-01",
          "max": "2024-12-31"
        }
      ]
    },
    {
      "name": "orders",
      "rows": 15000,
      "columns": [
        {
          "name": "order_id",
          "type": "integer",
          "unique": true
        },
        {
          "name": "customer_id",
          "type": "integer",
          "foreign_key": "customers.customer_id"
        },
        {
          "name": "amount",
          "type": "decimal",
          "min": 10.0,
          "max": 1000.0
        }
      ]
    }
  ]
}
```

## 📊 Formatos de Saída Suportados

- CSV
- JSON
- Parquet
- Excel (XLSX)
- SQL Insert Statements

## 📖 Documentação Completa

Para informações mais detalhadas, consulte a [documentação completa](./docs/usage.md).

### Exemplos de Uso

- [Exemplo Básico](./examples/basic_example.py)
- [Uso Avançado](./examples/advanced_usage.py)

## 🧪 Testes

Execute os testes com:

```bash
pytest tests/ -v
```

## 🤝 Contribuições

Contribuições são bem-vindas! Para começar:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Siga o estilo de código PEP 8
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário
- Escreva commits em português claro

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](./LICENSE) para detalhes.

## 👨‍💻 Autor

**Rodrigo Aiosa**
- GitHub: [@RodrigoAiosa](https://github.com/RodrigoAiosa)

## 💬 Suporte

Tem dúvidas ou encontrou um bug? 

- 🐛 [Abra uma Issue](https://github.com/RodrigoAiosa/bi_data_generator/issues)
- 💌 [Envie um Email](mailto:your-email@example.com)

## 📚 Recursos Adicionais

- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/)

## 🙏 Agradecimentos

Agradecimentos especiais a todos os contribuidores e à comunidade de dados aberta.

---

**Última atualização:** Abril de 2026  
**Status:** ✅ Ativo
