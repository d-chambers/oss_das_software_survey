---
key: pypi/rbdss-pipeline
source: pypi
name: rbdss-pipeline
package: rbdss-pipeline
description: Pipeline LLM auditavel com MCDA, HITL, evals e observabilidade por fase.
registry_url: https://pypi.org/project/rbdss-pipeline/
version: 1.1.0
last_release: '2026-05-04'
repository_url: https://github.com/leotavo/resposta-llm-auditavel
repository_declared_in_metadata: true
license_stated: MIT
author: null
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# RB-DSS Pipeline

Pacote Python para definir, executar, auditar e integrar **pipelines LLMOps personalizaveis por tarefa**, com RB-DSS, MCDA e HITL.

O repositorio deve conter o **servico/SDK reutilizavel**. Projetos negociais concretos, solucoes Power Platform, evidencias operacionais e configuracoes de ambiente devem viver em repositorios/pastas proprias e consumir este pacote como dependencia.

O produto central sao os pipelines: suas fases, prompts, policies, gates HITL, providers, validacoes e criterios de decisao. `runs/`, `projects/` e `stages` sao apenas uma forma local de persistir ou organizar execucoes durante desenvolvimento e auditoria manual.

## Inclui

- Pipeline padrao de 10 fases (`ASK -> ... -> VALIDATE`)
- Base para pipelines customizados por perfil de tarefa
- Artefatos versionaveis (`artifacts/*.md` e `artifacts/*.yaml`)
- Motor de decisao MCDA v1.0.0 (`artifacts/schemas/mcda_weights.yaml`) — motor primario
- Motor legado RB-DSS em `artifacts/rb_dss.yaml` — mantido como fallback historico
- Matriz de modelos e contingencia de quota em `artifacts/model_orchestration.yaml`
- CLI para executar pipelines, validar auditoria e operar utilitarios locais

## Requisitos

- Python 3.11+

## Instalar

```bash
pip install -e .[dev]
```

## Executar pipeline (modo mock)

```bash
rbdss-pipeline run ^
  --objective "Criar politica de qualidade para respostas LLM" ^
  --context-file artifacts/runbooks/pipeline-chatgpt.md ^
  --task-mnemonic "politica-qualidade-llm" ^
  --provider mock
```

Saidas em `runs/<mnemonico-da-tarefa>/<timestamp>/`.
Cada run inclui `prompt_summary.md` com resumo sucinto dos prompts executados.
Cada run tambem registra `pipeline_spec.json` e `pipeline_run.json`, que materializam
os contratos centrais da execucao sem acoplar o pacote a um filesystem especifico.
Quando o CLI recebe `execution_config.json` (ou overrides), ele persiste
`execution_config.json` com a configuracao efetiva usada na execucao.

Para executar um pipeline customizado pela CLI:

```bash
rbdss-pipeline run ^
  --objective "Executar revisao de dominio" ^
  --context-file contexto.md ^
  --spec-file pipeline_spec.json ^
  --phase-handler-registry-ref "meu_projeto.pipeline:build_registry" ^
  --provider mock
```

Ou concentre a execucao em um arquivo unico:

```json
{
  "objective": "Executar revisao de dominio",
  "context_file": "contexto.md",
  "provider": "mock",
  "task_mnemonic": "revisao-dominio",
  "out_dir": "runs",
  "spec_file": "pipeline_spec.json",
  "phase_handler_registry_refs": ["meu_projeto.pipeline:build_registry"]
}
```

```bash
rbdss-pipeline run --execution-config execution_config.json
```

## Direcao Do Core

O core deve evoluir em torno de contratos de pipeline:

- `PipelineSpec`: definicao versionavel do pipeline de uma tarefa
- `TaskProfile`: perfil que seleciona fases, providers, policies e gates
- `PipelinePhase`: fase configuravel do pipeline
- `PipelineRuntime`: executor do pipeline
- `PipelineRun`: execucao auditavel de um pipeline
- `PolicySet`: regras RB-DSS/MCDA aplicaveis
- `HITLGate`: ponto de decisao humana

Persistencia, filesystem e integracoes externas sao detalhes de runtime.

Uso minimo como SDK:

```python
from rbdss_pipeline import PipelineRunner, PipelineSpec, default_pipeline_spec
from rbdss_pipeline.providers import MockProvider

spec: PipelineSpec = default_pipeline_spec()
runner = PipelineRunner(provider=MockProvider(), spec=spec)
```

O runner aceita `PipelineSpec` customizado para metadados, perfil, policies, gates
HITL e subconjuntos de fases. As fases devem respeitar a ordem e as dependencias do
pipeline default; por exemplo, `ASK` pode rodar sozinho, enquanto `AUDIT` exige as
fases anteriores necessarias para produzir a resposta corrigida.

Handlers de fases conhecidas podem ser substituidos no runtime com um mapa simples
ou com `PhaseHandlerRegistry`, que permite empacotar handlers reutilizaveis por
tarefa, dominio ou projeto.

Fases customizadas tambem podem ser declaradas por string em `PipelineSpec.phases`,
desde que exista handler registrado e dependencias declaradas em `phase_dependencies`.

```python
from rbdss_pipeline import PhaseHandlerRegistry, PipelineRunner

registry = PhaseHandlerRegistry()
registry.register("domain_review", meu_handler)

runner = PipelineRunner(provider=provider, spec=spec, phase_handlers=registry)
```

Projetos consumidores tambem podem expor um factory Python e deixar o runner
carregar o registry por referencia configuravel:

```python
runner = PipelineRunner(
    provider=provider,
    spec=spec,
    phase_handler_registry_refs=["meu_projeto.pipeline:build_registry"],
)
```

## Adapter Local De Projeto

Os comandos abaixo existem para uso local em filesystem. Eles sao convenientes para prototipar e auditar manualmente, mas nao representam o contrato central do pacote.

```bash
rbdss-pipeline create-project ^
  --project-id "app-distribuicao-peticoes-gqmed" ^
  --project-name "Distribuicao de Peticoes GQMED" ^
  --objetivo "Apoiar distribuicao e triagem de peticoes" ^
  --contexto "Projeto operacional separado do pacote do pipeline" ^
  --projects-dir "../app-distribuicao-peticoes-gqmed/projects"
```

Em integracoes reais, um projeto pode persistir `PipelineRun` e `AuditEvent` em SharePoint, Dataverse, GitHub, banco relacional, filas ou outro orquestrador.

```bash
rbdss-pipeline add-stage ^
  --project-id "app-distribuicao-peticoes-gqmed" ^
  --stage-id "APP-DATA-01" ^
  --objetivo "Gerar dataset deduplicado" ^
  --instancia-pipeline-sugerida "PLAN -> SHAPE" ^
  --projects-dir "../app-distribuicao-peticoes-gqmed/projects"
```

```bash
rbdss-pipeline materialize-stage ^
  --project-id "app-distribuicao-peticoes-gqmed" ^
  --stage-id "APP-DATA-01" ^
  --run-path "runs/app-data-01/20260503" ^
  --projects-dir "../app-distribuicao-peticoes-gqmed/proje
