---
key: pypi/central-das-emendas-teste
source: pypi
name: central-das-emendas-teste
package: central-das-emendas-teste
description: Baixa e carrega em DataFrame o CSV de emendas do Google Drive
registry_url: https://pypi.org/project/central-das-emendas-teste/
version: 0.1.0
last_release: '2025-07-13'
repository_url: null
repository_declared_in_metadata: false
license_stated: MIT
author: Caio Sousa <c.sousa@poli.ufrj.br>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

\# central\_das\_emendas\_teste



Pequena biblioteca que baixa o CSV da \*\*Central das Emendas\*\* (hospedado

no Google Drive) e devolve um `pandas.DataFrame`.



\## Instalação para desenvolvedores



```bash

git clone https://github.com/SEU\_USUARIO/central\_das\_emendas\_teste.git

cd central\_das\_emendas\_teste

pip install -e .

#
