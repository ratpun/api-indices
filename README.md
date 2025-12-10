# Api-indices

Projeto em Python para geração de série histórica de índices econômicos acumulados (Fatores de Correção Monetária).

O sistema coleta dados automaticamente de fontes oficiais (**IBGE, Banco Central/Ipeadata e FIPE**), realiza o cálculo dos fatores acumulados mensais desde **Janeiro de 2007** até o mês atual e exporta o resultado consolidado em formato JSON.

Este projeto foi desenhado para simular correções de débitos e atualizações monetárias, replicando metodologias utilizadas por órgãos oficiais (como a Receita Federal para a SELIC e o IBGE para índices de preços).

## Índices Suportados e Metodologia

| Índice | Fonte de Dados | Metodologia de Cálculo Acumulado |
| :--- | :--- | :--- |
| **SELIC** | Banco Central (via Ipeadata) | **Soma Simples (Juros de Mora)**.<br>Padrão Sicalc/Receita Federal:<br>1. Mês do pagamento (atual) = 1%.<br>2. Mês anterior ao pagamento = Taxa Selic do mês.<br>3. Meses anteriores = Soma simples das taxas. |
| **IPCA** | IBGE (API SIDRA) | **Número-Índice**.<br>Cálculo via divisão da série histórica de número-índice (Base Fixa).<br>Fórmula: `(Índice Atual / Índice Data Base) - 1`. |
| **INPC** | IBGE (API SIDRA) | **Número-Índice**.<br>Mesma metodologia do IPCA. |
| **IPCA-E** | IBGE (API SIDRA) | **Número-Índice**.<br>Baseado na série histórica do IPCA-15. |
| **IPC-FIPE** | FIPE | **Número-Índice**.<br>Coleta direta da série histórica do índice geral da FIPE. |
| **IGP-M** | FGV (via Ipeadata) | **Produtório (Juros Compostos)**.<br>Acumulado das taxas mensais percentuais. |
| **TR** | Banco Central (via Ipeadata) | **Produtório (Juros Compostos)**.<br>Acumulado das taxas mensais da Taxa Referencial. |
| **Poupança** | Banco Central (via Ipeadata) | **Produtório (Juros Compostos)**.<br>Acumulado dos rendimentos mensais da poupança. |

##  Como Executar

### Pré-requisitos

*   Python 3.8 ou superior
*   Gerenciador de pacotes `pip`

### Instalação

1.  Clone este repositório.
2.  Instale as dependências necessárias listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Execução

Para gerar o arquivo JSON atualizado, execute o script principal:

```bash
python main.py
```

O script realizará os seguintes passos:
1.  Conexão com a API do **Ipeadata** (SELIC, TR, IGP-M, Poupança).
2.  Conexão com a API SIDRA do **IBGE** (IPCA, INPC, IPCA-E).
3.  Conexão com a API da **FIPE** (IPC).
4.  Cálculo dos acumulados reversos (de cada mês histórico até a data de hoje).
5.  Geração do arquivo `indices_acumulados.json` no diretório raiz (ou no caminho configurado).

## Estrutura do Projeto

O projeto foi modularizado para facilitar a manutenção e a escalabilidade de novas fontes de dados:

*   `main.py`: Arquivo principal. Gerencia a orquestração das chamadas, realiza os cálculos matemáticos dos acumulados e exporta o JSON.
*   `service_ibge.py`: Módulo responsável por buscar as séries de **Números-Índices** na API SIDRA.
*   `service_ipea.py`: Módulo responsável por buscar as séries de **Taxas Mensais** no Ipeadata.
*   `service_fipe.py`: Módulo responsável por iterar e buscar a série histórica no site da FIPE.
*   `requirements.txt`: Lista de bibliotecas Python necessárias (`pandas`, `numpy`, `requests`, `ipeadatapy`).

## Formato de Saída (JSON)

O arquivo gerado (`indices_acumulados.json`) contém um array de objetos. Cada objeto representa a referência mensal e os fatores acumulados para correção de um valor daquela data até o presente.

Exemplo:

```json
[
    {
        "Ano": 2024,
        "Mes": 11,
        "Referencia": "11/2024",
        "SELIC": 14.18,      
        "TR": 2.1239,
        "INPC": 4.4902,
        "IPCA": 4.6807,
        "IPCAE": 5.1523,
        "IGPM": 1.1967,
        "Poupanca": 9.5096,
        "IPC_FIPE": 5.0721
    },

]
```

*Nota: Os valores representam a porcentagem acumulada (%). Ex: 14.18 significa 14,18% de correção.*

---
Desenvolvido com Python e Pandas.
