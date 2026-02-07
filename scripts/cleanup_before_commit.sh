#!/bin/bash
# Limpeza antes de commit no GitHub

echo "🧹 Limpando arquivos temporários e sensíveis..."

# Remove __pycache__
echo "Removendo __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc
echo "Removendo .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove logs (mas mantém a pasta)
echo "Limpando logs..."
rm -rf airflow/logs/*
rm -rf dbt/logs/*
rm -rf dbt/target/*

# Remove .DS_Store (Mac)
echo "Removendo .DS_Store..."
find . -name ".DS_Store" -delete 2>/dev/null

# Remove arquivos temporários
echo "Removendo arquivos temporários..."
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null

# Cria pastas vazias se necessário
mkdir -p airflow/logs
mkdir -p dbt/logs
mkdir -p dbt/target

# Cria .gitkeep para manter pastas vazias
touch airflow/logs/.gitkeep
touch dbt/logs/.gitkeep
touch dbt/target/.gitkeep

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📋 CHECKLIST antes do git push:"
echo "  [✓] Logs removidos"
echo "  [✓] __pycache__ removido"
echo "  [✓] .pyc removidos"
echo "  [✓] Arquivos temporários removidos"
echo ""
echo "⚠️  VERIFIQUE MANUALMENTE:"
echo "  [ ] .env não está commitado"
echo "  [ ] Não há credenciais no código"
echo "  [ ] .env.example está atualizado"
echo "  [ ] README.md está correto"
echo "  [ ] LICENSE existe"
echo ""
