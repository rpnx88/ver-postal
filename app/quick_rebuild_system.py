#!/usr/bin/env python3
"""
Sistema de Rebuild Rápido do Dashboard
Versão otimizada que usa build existente e apenas atualiza o pacote de deploy
"""

import os
import sys
import json
import hashlib
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path

# Configurações
PROJECT_ROOT = "/home/ubuntu/dashboard_indicacoes"
APP_DIR = f"{PROJECT_ROOT}/app"
JSON_FILE = f"{APP_DIR}/public/dashboard_data.json"
HASH_FILE = f"{PROJECT_ROOT}/.last_json_hash"
LOG_DIR = f"{PROJECT_ROOT}/.logs"
DEPLOY_DIR = f"{PROJECT_ROOT}/.deploy"

# Configurar logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = f"{LOG_DIR}/quick_rebuild_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class QuickRebuildSystem:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.app_dir = APP_DIR
        self.json_file = JSON_FILE
        self.hash_file = HASH_FILE
        self.deploy_dir = DEPLOY_DIR
        
    def calculate_file_hash(self, file_path):
        """Calcula hash MD5 do arquivo para detectar mudanças"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except FileNotFoundError:
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {e}")
            return None
    
    def get_last_hash(self):
        """Recupera o último hash salvo"""
        try:
            if os.path.exists(self.hash_file):
                with open(self.hash_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Erro ao ler último hash: {e}")
        return None
    
    def save_hash(self, hash_value):
        """Salva o hash atual"""
        try:
            with open(self.hash_file, 'w') as f:
                f.write(hash_value)
            logger.info(f"Hash salvo: {hash_value}")
        except Exception as e:
            logger.error(f"Erro ao salvar hash: {e}")
    
    def has_file_changed(self):
        """Verifica se o arquivo JSON foi modificado"""
        if not os.path.exists(self.json_file):
            logger.warning(f"Arquivo JSON não existe: {self.json_file}")
            return False
        
        current_hash = self.calculate_file_hash(self.json_file)
        if current_hash is None:
            return False
        
        last_hash = self.get_last_hash()
        
        if last_hash is None:
            logger.info("Primeiro run - salvando hash inicial")
            self.save_hash(current_hash)
            return False
        
        if current_hash != last_hash:
            logger.info(f"Mudança detectada! Hash anterior: {last_hash}, Hash atual: {current_hash}")
            return True
        
        return False
    
    def run_command(self, command, cwd=None):
        """Executa comando e retorna resultado"""
        try:
            logger.info(f"Executando: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.app_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Comando executado com sucesso: {command}")
                return True, result.stdout
            else:
                logger.error(f"Erro no comando: {command}")
                logger.error(f"Error output: {result.stderr}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout no comando: {command}")
            return False, "Timeout"
        except Exception as e:
            logger.error(f"Exceção ao executar comando: {e}")
            return False, str(e)
    
    def backup_current_deploy(self):
        """Faz backup do deploy atual"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.deploy_dir}/app_backup_{timestamp}.tgz"
            
            if os.path.exists(f"{self.deploy_dir}/app.tgz"):
                os.rename(f"{self.deploy_dir}/app.tgz", backup_file)
                logger.info(f"Backup criado: {backup_file}")
                
        except Exception as e:
            logger.error(f"Erro ao fazer backup: {e}")
    
    def update_json_in_build(self):
        """Atualiza o JSON no build existente sem rebuild completo"""
        logger.info("=== ATUALIZANDO JSON NO BUILD EXISTENTE ===")
        
        build_dir = f"{self.app_dir}/.next"
        build_json_path = f"{build_dir}/static/dashboard_data.json"
        
        # Verificar se existe build
        if not os.path.exists(build_dir):
            logger.error("Build não encontrado - executando build completo")
            return self.full_rebuild()
        
        # Copiar JSON atualizado para o build
        try:
            # Criar diretório static se não existir
            static_dir = f"{build_dir}/static"
            os.makedirs(static_dir, exist_ok=True)
            
            # Copiar JSON atualizado
            success, _ = self.run_command(f"cp {self.json_file} {build_json_path}")
            if not success:
                logger.error("Falha ao copiar JSON para build")
                return False
            
            logger.info("JSON atualizado no build existente")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar JSON no build: {e}")
            return False
    
    def full_rebuild(self):
        """Executa rebuild completo apenas se necessário"""
        logger.info("=== EXECUTANDO REBUILD COMPLETO ===")
        
        # Limpar build anterior
        success, _ = self.run_command("rm -rf .next")
        if not success:
            logger.warning("Falha ao limpar build anterior")
        
        # Executar build
        success, output = self.run_command("npm run build")
        if not success:
            logger.error("Falha no build da aplicação")
            return False
        
        logger.info("Build completo concluído")
        return True
    
    def create_deployment_package(self):
        """Cria pacote de deployment usando build existente"""
        logger.info("=== CRIANDO PACOTE DE DEPLOYMENT ===")
        
        os.makedirs(self.deploy_dir, exist_ok=True)
        
        # Fazer backup do deploy atual
        self.backup_current_deploy()
        
        # Verificar se existe build
        build_dir = f"{self.app_dir}/.next"
        if not os.path.exists(build_dir):
            logger.error("Build não encontrado")
            return False
        
        # Criar novo pacote
        success, output = self.run_command(
            f"tar -czf {self.deploy_dir}/app.tgz -C {build_dir} .",
            cwd=self.project_root
        )
        
        if not success:
            logger.error("Falha ao criar pacote de deployment")
            return False
        
        logger.info(f"Pacote de deployment criado: {self.deploy_dir}/app.tgz")
        return True
    
    def get_deployment_info(self):
        """Obtém informações do deployment"""
        try:
            if os.path.exists(f"{self.deploy_dir}/app.tgz"):
                stat = os.stat(f"{self.deploy_dir}/app.tgz")
                size_mb = stat.st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                return {
                    'size_mb': round(size_mb, 2),
                    'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
                    'exists': True
                }
        except Exception as e:
            logger.error(f"Erro ao obter info do deployment: {e}")
        
        return {'exists': False}
    
    def quick_rebuild(self):
        """Executa rebuild rápido usando build existente"""
        logger.info("🚀 INICIANDO REBUILD RÁPIDO")
        start_time = time.time()
        
        try:
            # 1. Atualizar JSON no build existente (rápido)
            if not self.update_json_in_build():
                logger.warning("Falha na atualização rápida - tentando rebuild completo")
                if not self.full_rebuild():
                    logger.error("❌ Falha no rebuild completo")
                    return False
            
            # 2. Criar pacote de deployment
            if not self.create_deployment_package():
                logger.error("❌ Falha ao criar pacote")
                return False
            
            # 3. Atualizar hash
            current_hash = self.calculate_file_hash(self.json_file)
            if current_hash:
                self.save_hash(current_hash)
            
            # 4. Log de sucesso
            elapsed_time = time.time() - start_time
            deploy_info = self.get_deployment_info()
            
            logger.info("✅ REBUILD RÁPIDO CONCLUÍDO!")
            logger.info(f"⏱️  Tempo total: {elapsed_time:.2f} segundos")
            logger.info(f"📦 Tamanho do pacote: {deploy_info.get('size_mb', 'N/A')} MB")
            logger.info(f"🕒 Deployment atualizado: {deploy_info.get('modified', 'N/A')}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante rebuild rápido: {e}")
            return False
    
    def monitor_and_rebuild(self):
        """Monitora mudanças e executa rebuild rápido quando necessário"""
        logger.info("🔍 Verificando mudanças no dashboard_data.json...")
        
        if self.has_file_changed():
            logger.info("📝 Mudança detectada - iniciando rebuild rápido...")
            success = self.quick_rebuild()
            
            if success:
                logger.info("✅ Sistema atualizado com sucesso!")
                return True
            else:
                logger.error("❌ Falha no rebuild rápido")
                return False
        else:
            logger.info("✅ Nenhuma mudança detectada")
            return True

def main():
    """Função principal"""
    system = QuickRebuildSystem()
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--force':
            logger.info("Modo: Rebuild rápido forçado")
            success = system.quick_rebuild()
        elif sys.argv[1] == '--status':
            logger.info("Modo: Verificação de status")
            deploy_info = system.get_deployment_info()
            if deploy_info['exists']:
                logger.info(f"📦 Deploy atual: {deploy_info['size_mb']} MB, modificado em {deploy_info['modified']}")
            else:
                logger.info("❌ Nenhum deploy encontrado")
            success = True
        else:
            logger.error(f"Argumento inválido: {sys.argv[1]}")
            logger.info("Uso: python3 quick_rebuild_system.py [--force|--status]")
            success = False
    else:
        logger.info("Modo: Monitoramento automático")
        success = system.monitor_and_rebuild()
    
    if success:
        logger.info("🎉 Operação concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("💥 Operação falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
