#!/bin/bash
# Script de Configuração do Sistema de Rebuild Automático
# Configura e testa o sistema completo

set -e

PROJECT_ROOT="/home/ubuntu/dashboard_indicacoes"
SCRIPT_FILE="$PROJECT_ROOT/auto_rebuild_system.py"

echo "🚀 Configurando Sistema de Rebuild Automático..."

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p "$PROJECT_ROOT/.logs"
mkdir -p "$PROJECT_ROOT/.deploy"

# Tornar script executável
echo "🔧 Configurando permissões..."
chmod +x "$SCRIPT_FILE"

# Verificar dependências
echo "🔍 Verificando dependências..."
cd "$PROJECT_ROOT/app"

if [ ! -d "node_modules" ]; then
    echo "❌ node_modules não encontrado. Execute 'npm install' primeiro."
    exit 1
fi

if [ ! -f "public/dashboard_data.json" ]; then
    echo "❌ dashboard_data.json não encontrado."
    exit 1
fi

echo "✅ Dependências verificadas"

# Teste inicial do sistema
echo "🧪 Executando teste inicial..."
python3 "$SCRIPT_FILE" --status

echo ""
echo "🎉 Sistema configurado com sucesso!"
echo ""
echo "📋 Comandos disponíveis:"
echo "  • Monitoramento automático: python3 $SCRIPT_FILE"
echo "  • Rebuild forçado:          python3 $SCRIPT_FILE --force"
echo "  • Status do sistema:        python3 $SCRIPT_FILE --status"
echo ""
echo "📝 Logs disponíveis em: $PROJECT_ROOT/.logs/"
echo "📦 Deploys salvos em:   $PROJECT_ROOT/.deploy/"
