#!/usr/bin/env python3
"""
Monitor de Mudanças e Rebuild Automático - Versão Simplificada
Detecta mudanças no dashboard_data.json e triggera rebuild quando necessário
"""

import os
import sys
import hashlib
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configurações
PROJECT_ROOT = "/home/ubuntu/dashboard_indicacoes"
APP_DIR = f"{PROJECT_ROOT}/app"
JSON_FILE = f"{APP_DIR}/public/dashboard_data.json"
HASH_FILE = f"{PROJECT_ROOT}/.last_json_hash"
LOG_DIR = f"{PROJECT_ROOT}/.logs"

# Configurar logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = f"{LOG_DIR}/monitor_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def calculate_file_hash(file_path):
    """Calcula hash MD5 do arquivo"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()
    except Exception as e:
        logger.error(f"Erro ao calcular hash: {e}")
        return None

def get_last_hash():
    """Recupera o último hash salvo"""
    try:
        if os.path.exists(HASH_FILE):
            with open(HASH_FILE, 'r') as f:
                return f.read().strip()
    except Exception as e:
        logger.error(f"Erro ao ler último hash: {e}")
    return None

def save_hash(hash_value):
    """Salva o hash atual"""
    try:
        with open(HASH_FILE, 'w') as f:
            f.write(hash_value)
        logger.info(f"Hash salvo: {hash_value}")
    except Exception as e:
        logger.error(f"Erro ao salvar hash: {e}")

def has_file_changed():
    """Verifica se o arquivo JSON foi modificado"""
    if not os.path.exists(JSON_FILE):
        logger.warning(f"Arquivo JSON não existe: {JSON_FILE}")
        return False
    
    current_hash = calculate_file_hash(JSON_FILE)
    if current_hash is None:
        return False
    
    last_hash = get_last_hash()
    
    if last_hash is None:
        logger.info("Primeiro run - salvando hash inicial")
        save_hash(current_hash)
        return False
    
    if current_hash != last_hash:
        logger.info(f"🔥 MUDANÇA DETECTADA!")
        logger.info(f"Hash anterior: {last_hash}")
        logger.info(f"Hash atual: {current_hash}")
        return True
    
    return False

def trigger_rebuild():
    """Triggera o rebuild usando o sistema principal"""
    try:
        logger.info("🚀 Triggerando rebuild automático...")
        
        # Executar o sistema rápido de rebuild
        result = subprocess.run([
            'python3', 
            f'{PROJECT_ROOT}/quick_rebuild_system.py', 
            '--force'
        ], 
        capture_output=True, 
        text=True,
        timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ Rebuild executado com sucesso!")
            
            # Atualizar hash após rebuild bem-sucedido
            current_hash = calculate_file_hash(JSON_FILE)
            if current_hash:
                save_hash(current_hash)
            
            return True
        else:
            logger.error("❌ Falha no rebuild")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("⏰ Timeout no rebuild (30 min)")
        return False
    except Exception as e:
        logger.error(f"💥 Erro ao executar rebuild: {e}")
        return False

def main():
    """Função principal de monitoramento"""
    logger.info("🔍 Iniciando monitoramento de mudanças...")
    logger.info(f"📁 Monitorando: {JSON_FILE}")
    
    try:
        if has_file_changed():
            logger.info("📝 Mudança detectada - iniciando processo de rebuild...")
            success = trigger_rebuild()
            
            if success:
                logger.info("🎉 Sistema atualizado com sucesso!")
                return True
            else:
                logger.error("💥 Falha na atualização do sistema")
                return False
        else:
            logger.info("✅ Nenhuma mudança detectada - sistema atualizado")
            return True
            
    except Exception as e:
        logger.error(f"💥 Erro no monitoramento: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
