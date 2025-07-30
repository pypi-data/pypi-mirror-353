# Gestão de Imóveis 🏠

Projeto desenvolvido por:  
**Gonçalo José Madureira Tavares**  
**Guilherme Costa e Silva**  
**João Miguel Sernadas Maia**  
**Vasco Nogueira Azevedo**

## 📅 Datas
- **Início:** 12.03.2025  
- **Fim:** 24.04.2025

---

## 📌 Descrição

Este projeto tem como objetivo a criação de um sistema de **gestão de dados de imóveis e clientes**, permitindo adicionar, remover, listar e associar clientes a imóveis de forma eficiente e organizada.

---

## 🔧 Funcionalidades

### 📇 Gestão de Clientes
- Adicionar novo cliente com os dados:
  - Nome
  - Email
  - Telefone
  - NIF
- Remover cliente pelo nome
- Listar todos os clientes com as casas atribuídas
- Atribuir casas específicas a clientes existentes
- Validação para evitar duplicações de clientes

### 🏡 Gestão de Imóveis
- Adicionar novo imóvel com os dados:
  - Nome
  - Localização
  - Rua
  - Tipo (ex: T1, T2, T3)
  - Certificação energética
  - Mobilidade reduzida (True/False)
  - Data de construção
  - Tipo de construção
  - Despesas de construção
  - Latitude e Longitude
- Remover imóveis existentes
- Listar todos os imóveis com todos os seus detalhes
- Validação para evitar duplicações de imóveis

---

## 🧪 Exemplos de Uso

```python
# Inicialização
sistema = SistemaClientes()
imobiliaria = Imobiliaria()

# Adicionar clientes
sistema.adicionar_cliente("João Silva", "joao@email.com", "999999999", "123456789")

# Adicionar imóveis
imobiliaria.adicionar_casa("Casa do Lago", "Lisboa", "Rua do Sobreiro", "T3", "A+", True,
                            "2005-06-15", "Madeira", "85000", 38.7169, -9.1399)

# Atribuir imóveis a clientes
sistema.atribuir_casa("João Silva", "Casa do Lago", imobiliaria)

# Listar clientes e imóveis
sistema.listar_clientes()
imobiliaria.listar_casas()
```

---

## 🚫 Tratamento de Erros
- Erros ao adicionar clientes ou casas duplicadas
- Erros ao tentar remover elementos inexistentes
- Prevenção de atribuição repetida da mesma casa ao mesmo cliente

---

## 📁 Estrutura do Projeto

```
GestaoImoveis/
├── gestao_imoveis.py   # Código principal com as classes e métodos
├── README.md           # Este ficheiro
```

---

## ✅ Requisitos
- Python 3.x
- Sem dependências externas (bibliotecas padrão do Python)

---

## 📜 Licença
Este projeto foi desenvolvido para fins educativos e não possui licença comercial.
