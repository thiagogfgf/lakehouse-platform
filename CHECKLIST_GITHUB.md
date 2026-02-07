# ✅ Checklist - Antes de Publicar no GitHub

## 🔒 Segurança e Privacidade

- [ ] **`.env` não está commitado** (verificar: `git status | grep .env`)
- [ ] **Não há credenciais no código** (API keys, passwords, tokens)
- [ ] **Não há dados pessoais** ou sensíveis
- [ ] **`.env.example` está atualizado** com todas as variáveis necessárias
- [ ] **Credenciais padrão estão seguras** (ex: minioadmin é apenas para dev local)

## 📝 Documentação

- [ ] **README.md está completo e atualizado**
  - Instruções de setup claras
  - Pré-requisitos listados
  - Quick start funcional
  - Links para outras docs

- [ ] **SETUP_YOUR_PIPELINE.md está completo**
  - Guia passo a passo de customização
  - Exemplos funcionais
  - Troubleshooting

- [ ] **LICENSE existe** e está correto

- [ ] **CONTRIBUTING.md** (se aplicável)

## 🧹 Limpeza de Arquivos

- [ ] **Logs removidos do git**
  - `airflow/logs/` (no .gitignore)
  - `dbt/logs/` (no .gitignore)
  - `dbt/target/` (no .gitignore)

- [ ] **__pycache__ removido**
  - Execute: `find . -name "__pycache__" -type d`

- [ ] **.pyc removidos**
  - Execute: `find . -name "*.pyc"`

- [ ] **Dados de teste/exemplo não commitados**
  - `*.parquet`, `*.csv` (no .gitignore)

- [ ] **Arquivos temporários removidos**
  - `.DS_Store`, `*.tmp`, `*~`

## ⚙️ Configuração

- [ ] **docker-compose.yml está genérico**
  - Sem paths absolutos específicos da máquina
  - Variáveis via .env

- [ ] **Portas não estão em conflito**
  - Documentadas no README

- [ ] **Volumes configurados corretamente**
  - Dados não são hard-linkados

## 🧪 Testes

- [ ] **Template funciona do zero**
  ```bash
  git clone <repo> test-lakehouse
  cd test-lakehouse
  cp .env.example .env
  docker compose up -d
  # Verificar se todos os containers sobem
  ```

- [ ] **Scripts de exemplo funcionam**
  ```bash
  # Se manteve exemplos
  cp examples/scripts/ingest_nyc_taxi.py scripts/
  docker exec airflow-webserver python3 /opt/airflow/scripts/ingest_nyc_taxi.py
  ```

- [ ] **Documentação está correta**
  - Links funcionam
  - Comandos estão corretos
  - Paths existem

## 📁 Estrutura

- [ ] **Pastas vazias têm .gitkeep** (se necessário)
- [ ] **Arquivos template estão em `templates/`**
- [ ] **Exemplos estão em `examples/`**
- [ ] **Docs antigas em `docs/archive/`**

## 🚀 Git

- [ ] **.gitignore completo e testado**
  ```bash
  git status
  # Verificar se não aparece .env, logs, __pycache__, etc
  ```

- [ ] **Não há arquivos grandes** (>50MB)
  ```bash
  find . -type f -size +50M
  ```

- [ ] **Commits têm mensagens descritivas**

- [ ] **Branch main está limpo e estável**

## 📊 GitHub Repository Settings

Depois de fazer o push:

- [ ] **Description clara no repositório**
  - "Data Lakehouse Template with Trino, Iceberg, MinIO, dbt & Airflow"

- [ ] **Topics/Tags adicionados**
  - `data-engineering`, `lakehouse`, `trino`, `iceberg`, `dbt`, `airflow`, `docker`, `template`

- [ ] **README.md renderiza corretamente**
  - Diagramas aparecem
  - Links funcionam

- [ ] **LICENSE visível no GitHub**

- [ ] **Seção About configurada**
  - Website (se tiver)
  - Topics

- [ ] **.github/workflows/** (se usar CI/CD)

## 🎯 Opcional mas Recomendado

- [ ] **GitHub Actions para CI/CD**
  - Lint Python
  - Validar docker-compose
  - Teste de build

- [ ] **Issue templates** (`.github/ISSUE_TEMPLATE/`)
  - Bug report
  - Feature request

- [ ] **Pull Request template**

- [ ] **CHANGELOG.md**

- [ ] **Screenshots/GIFs** no README
  - Airflow UI
  - Trino UI
  - dbt docs

- [ ] **Badge shields no README**
  - License
  - Docker
  - GitHub stars

---

## 🚀 Comandos Finais

```bash
# 1. Verificar status
git status

# 2. Verificar o que vai ser commitado
git add -n .

# 3. Remover arquivos sensíveis se aparecerem
git rm --cached <arquivo>

# 4. Commit
git add .
git commit -m "feat: initial commit - lakehouse template"

# 5. Push
git push origin main
```

---

## ✅ Teste Final Pós-Push

Faça um teste completo clonando o repo do GitHub:

```bash
# Em outro diretório
git clone https://github.com/seu-usuario/distributed-lakehouse.git test
cd test

# Verifique se funciona do zero
cp .env.example .env
docker compose up -d
docker compose ps

# Teste customização básica
cp templates/ingest_template.py scripts/ingest_my_data.py
# ... customize e teste
```

---

**Tudo OK?** 🎉 **Repositório pronto para ser usado como template!**
