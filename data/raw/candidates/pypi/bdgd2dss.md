---
key: pypi/bdgd2dss
source: pypi
name: bdgd2dss
package: bdgd2dss
description: Ferramenta para modelagem de alimentadores da BDGD para uso com OpenDSS
registry_url: https://pypi.org/project/bdgd2dss/
version: 0.0.9
last_release: '2026-05-08'
repository_url: null
repository_declared_in_metadata: false
license_stated: MIT License
author: Arthur Gomes de Souza
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

<!-- References (Formatting): -->
<!-- https://portal.revendadesoftware.com.br/manuais/base-de-conhecimento/sintaxe-markdown -->
<!-- https://docs.github.com/en/enterprise-cloud@latest/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax -->

![PyPI](https://img.shields.io/pypi/v/bdgd2dss)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-brightgreen)
![License](https://img.shields.io/github/license/ArthurGS97/bdgd2dss)
![Downloads](https://static.pepy.tech/badge/bdgd2dss)

<div align="center">
  <img src="https://raw.githubusercontent.com/ArthurGS97/bdgd2dss/main/Prints_git/icon.png" width="120">
</div>

# bdgd2dss

Conjunto de arquivos referente à biblioteca **bdgd2dss** desenvolvida na linguagem *Python*, que transforma as planilhas oriundas da Base de Dados Geográfica da Distribuidora (BDGD) em arquivos *.dss* para simulação e estudos de alimentadores de sistemas de distribuição de energia elétrica no ambiente *OpenDSS*. A ferramenta em questão foi criada pelo Mestrando em Engenharia Elétrica Arthur Gomes de Souza, que desenvolve pesquisas com o foco em proteção de sistemas elétricos de potência, sob orientação do prof. Dr. Wellington Maycon Santos Bernardes (Universidade Federal de Uberlândia).

Instalação
------------

Para instalar e utilizar a biblioteca **bdgd2dss**, siga os passos abaixo. Recomenda-se iniciar criando um ambiente virtual no terminal do VSCode para isolar as dependências do projeto.

1. Criar o ambiente virtual:

    ```bash
    python -m venv .venv
    ```

2. Ativar o Ambiente Virtual:

    ```bash
    .venv\Scripts\Activate
    ```

3. Instalando a biblioteca:

    ```bash
    pip install bdgd2dss
    ```

4. A seguir, são apresentados os procedimentos para exportação dos dados e a utilização da biblioteca. Serão detalhadas a estrutura da base de dados e as instruções para seu uso em conjunto com a biblioteca.

   
## 1 - Base de Dados Geográfica da Distribuidora - BDGD

A BDGD faz parte integrante do Sistema de Informação Geográfico Regulatório da Distribuição (SIG-R). Em adição, é um modelo geográfico estabelecido com o objetivo de representar de forma simplificada o sistema elétrico real da distribuidora, visando refletir tanto a situação real dos ativos quanto as informações técnicas e comerciais de interesse. De forma a emular a rede elétrica dos agentes envolvidos, a BDGD é estruturada em entidades, modelos abstratos de dados estabelecidos com o objetivo de representar informações importantes, como as perdas estimadas pelos agentes. Cada uma dessas entidades é detalhada em diversos dados, dentre as quais constam aquelas que devem observar a codificação pré-estabelecida pelo Dicionário de Dados da Agência Nacional de Energia Elétrica (ANEEL) (DDA), o qual especifica padrões de dados a serem utilizados na BDGD, visando a normalização das informações. Em relação aos dados cartográficos, eles são disponibilizados em um arquivo *Geodatabase* (*.gdb*), por distribuidora. O Manual de Instruções da BDGD (https://www.gov.br/aneel/pt-br/centrais-de-conteudos/manuais-modelos-e-instrucoes/distribuicao) e o Módulo 10 do PRODIST (https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/prodist) contém informações úteis para entender a BDGD, como as entidades disponibilizadas e as definições dos campos [1]. 

Inicialmente, os dados da BDGD são classificados como entidades geográficas e não geográficas, as Tabelas 1 e 2 mostram as camadas que as compõe, respectivamente.


**Tabela 1: Entidades geográficas da BDGD.** 
| id  | Sigla  | Nome                                                       |
|-----|--------|------------------------------------------------------------|
| 22  | ARAT   | Área e Atuação                                             |
| 23  | CONJ   | Conjunto                                                   |
| 24  | PONNOT | Ponto Notável                                              |
| 25  | SSDAT  | Segmento do Sistema de Distribuição de Alta Tensão         |
| 26  | SSDBT  | Segmento do Sistema de Distribuição de Baixa Tensão        |
| 27  | SSDMT  | Segmento do Sistema de Distribuição de Média Tensão        |
| 28  | SUB    | Subestação                                                 |
| 38  | UNCRAT | Unidade Compensadora de Reativo de Alta Tensão             |
| 29  | UNCRBT | Unidade Compensadora de Reativo de Baixa Tensão            |
| 30  | UNCRMT | Unidade Compensadora de Reativo de Média Tensão            |
| 39  | UCAT   | Unidade Consumidora de Alta Tensão                         |
| 40  | UCBT   | Unidade Consumidora de Baixa Tensão                        |
| 41  | UCMT   | Unidade Consumidora de Média Tensão                        |
| 42  | UGAT   | Unidade Geradora de Alta Tensão                            |
| 43  | UGBT   | Unidade Geradora de Baixa Tensão                           |
| 44  | UGMT   | Unidade Geradora de Média Tensão                           |
| 31  | UNREAT | Unidade Reguladora de Alta Tensão                          |
| 32  | UNREMT | Unidade Reguladora de Média Tensão                         |
| 33  | UNSEAT | Unidade seccionadora de Alta Tensão                        |
| 34  | UNSEBT | Unidade seccionadora de Baixa Tensão                       |
| 35  | UNSEMT | Unidade seccionadora de Média Tensão                       |
| 36  | UNTRD  | Unidade Transformadora da Distribuição                     |
| 37  | UNTRS  | Unidade Transformadora da Subestação                       |

**Fonte:** Adaptado de ANEEL (2021) [2].

**Tabela 1: Entidades não geográficas da BDGD.**

| id  | Sigla   | Nome                                          |
|-----|---------|-----------------------------------------------|
| 3   | BE      | Balanço de Energia                            |
| 0   | BAR     | Barramento
