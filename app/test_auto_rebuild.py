#!/usr/bin/env python3
"""
Script de Teste do Sistema de Auto Rebuild
Simula mudanças no dashboard_data.json para testar o sistema
"""

import os
import json
import time
import subprocess
from datetime import datetime

PROJECT_ROOT = "/home/ubuntu/dashboard_indicacoes"
JSON_FILE = f"{PROJECT_ROOT}/app/public/dashboard_data.json"
BACKUP_FILE = f"{PROJECT_ROOT}/app/public/dashboard_data_backup.json"

def backup_original():
    """Faz backup do arquivo original"""
    if os.path.exists(JSON_FILE):
        subprocess.run(['cp', JSON_FILE, BACKUP_FILE])
        print(f"✅ Backup criado: {BACKUP_FILE}")

def restore_original():
    """Restaura o arquivo original"""
    if os.path.exists(BACKUP_FILE):
        subprocess.run(['cp', BACKUP_FILE, JSON_FILE])
        print(f"✅ Arquivo original restaurado")

def simulate_change():
    """Simula uma mudança no arquivo JSON"""
    try:
        # Ler arquivo atual
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        
        # Adicionar timestamp para simular mudança
        if 'metadata' not in data:
            data['metadata'] = {}
        
        data['metadata']['last_test_update'] = datetime.now().isoformat()
        data['metadata']['test_counter'] = data['metadata'].get('test_counter', 0) + 1
        
        # Salvar arquivo modificado
        with open(JSON_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Mudança simulada - contador: {data['metadata']['test_counter']}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao simular mudança: {e}")
        return False

def run_monitor():
    """Executa o monitor uma vez"""
    try:
        result = subprocess.run([
            'python3', 
            f'{PROJECT_ROOT}/monitor_and_rebuild.py'
        ], 
        capture_output=True, 
        text=True,
        timeout=60
        )
        
        print("📋 Output do monitor:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Erros:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar monitor: {e}")
        return False

def main():
    print("🧪 TESTE DO SISTEMA DE AUTO REBUILD")
    print("=" * 50)
    
    # 1. Fazer backup
    print("\n1. Fazendo backup do arquivo original...")
    backup_original()
    
    # 2. Executar monitor inicial (deve detectar que não há mudanças)
    print("\n2. Executando monitor inicial...")
    run_monitor()
    
    # 3. Simular mudança
    print("\n3. Simulando mudança no arquivo...")
    if not simulate_change():
        return
    
    # 4. Executar monitor novamente (deve detectar mudança)
    print("\n4. Executando monitor após mudança...")
    success = run_monitor()
    
    # 5. Restaurar original
    print("\n5. Restaurando arquivo original...")
    restore_original()
    
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Sistema de auto rebuild está funcionando corretamente")
    else:
        print("\n❌ TESTE FALHOU!")
        print("💥 Verifique os logs para mais detalhes")

if __name__ == "__main__":
    main()
