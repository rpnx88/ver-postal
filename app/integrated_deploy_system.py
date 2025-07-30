
#!/usr/bin/env python3
"""
Sistema Integrado de Deploy do Dashboard
Detecta mudanças no JSON e faz deploy usando o sistema NextJS existente
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
HASH_FILE = f"{PROJECT_ROOT}/monitoring_system/rebuild_state.json"
LOG_DIR = f"{PROJECT_ROOT}/monitoring_system/logs"

# Configurar logging
os.makedirs(LOG_DIR, exist_ok=True)
log_file = f"{LOG_DIR}/integrated_deploy_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class IntegratedDeploySystem:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.app_dir = APP_DIR
        self.json_file = JSON_FILE
        self.hash_file = HASH_FILE
        
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
    
    def get_rebuild_state(self):
        """Obtém o estado atual do rebuild"""
        try:
            if os.path.exists(self.hash_file):
                with open(self.hash_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Erro ao ler estado do rebuild: {e}")
            return {}
    
    def save_rebuild_state(self, hash_value):
        """Salva o estado atual do rebuild"""
        try:
            state = {
                "last_hash": hash_value,
                "last_check": datetime.now().isoformat(),
                "last_rebuild": datetime.now().isoformat()
            }
            with open(self.hash_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Estado do rebuild salvo: {hash_value}")
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
    
    def has_file_changed(self):
        """Verifica se o arquivo JSON foi modificado"""
        if not os.path.exists(self.json_file):
            logger.warning(f"Arquivo JSON não existe: {self.json_file}")
            return False
        
        current_hash = self.calculate_file_hash(self.json_file)
        if current_hash is None:
            return False
        
        state = self.get_rebuild_state()
        last_hash = state.get('last_hash')
        
        if last_hash is None:
            logger.info("Primeiro run - salvando hash inicial")
            self.save_rebuild_state(current_hash)
            return False
        
        if current_hash != last_hash:
            logger.info(f"Mudança detectada! Hash anterior: {last_hash}, Hash atual: {current_hash}")
            return True
        
        return False
    
    def run_command(self, command, cwd=None, timeout=300):
        """Executa comando e retorna resultado"""
        try:
            logger.info(f"Executando: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.app_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Comando executado com sucesso")
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
    
    def kill_existing_servers(self):
        """Mata servidores Next.js existentes"""
        try:
            # Mata processos do Next.js na porta 3000
            self.run_command("pkill -f 'next dev'", timeout=10)
            self.run_command("pkill -f 'next start'", timeout=10)
            self.run_command("lsof -ti:3000 | xargs kill -9", timeout=10)
            time.sleep(2)
            logger.info("Servidores existentes encerrados")
        except Exception as e:
            logger.warning(f"Erro ao encerrar servidores: {e}")
    
    def test_nextjs_project(self):
        """Testa o projeto NextJS usando a ferramenta integrada"""
        logger.info("=== TESTANDO PROJETO NEXTJS ===")
        
        # Usar a ferramenta de teste integrada
        test_command = f"cd {self.project_root} && python3 -c \""
        test_command += "import sys; sys.path.append('/opt/hostedapp'); "
        test_command += "from tools.test_nextjs_project import test_nextjs_project; "
        test_command += f"test_nextjs_project('{self.project_root}')\""
        
        success, output = self.run_command(test_command, cwd=None, timeout=600)
        
        if success:
            logger.info("Teste do projeto NextJS concluído com sucesso")
            return True
        else:
            logger.error("Falha no teste do projeto NextJS")
            return False
    
    def build_and_checkpoint(self):
        """Faz build e salva checkpoint usando a ferramenta integrada"""
        logger.info("=== FAZENDO BUILD E CHECKPOINT ===")
        
        # Usar a ferramenta de checkpoint integrada
        timestamp = datetime.now().strftime("%H:%M")
        checkpoint_command = f"cd {self.project_root} && python3 -c \""
        checkpoint_command += "import sys; sys.path.append('/opt/hostedapp'); "
        checkpoint_command += "from tools.build_and_save_nextjs_project_checkpoint import build_and_save_nextjs_project_checkpoint; "
        checkpoint_command += f"build_and_save_nextjs_project_checkpoint('{self.project_root}', 'Dashboard atualizado - {timestamp}')\""
        
        success, output = self.run_command(checkpoint_command, cwd=None, timeout=600)
        
        if success:
            logger.info("Build e checkpoint concluídos com sucesso")
            return True
        else:
            logger.error("Falha no build e checkpoint")
            return False
    
    def start_dev_server(self):
        """Inicia o servidor de desenvolvimento"""
        logger.info("=== INICIANDO SERVIDOR DE DESENVOLVIMENTO ===")
        
        # Matar servidores existentes
        self.kill_existing_servers()
        
        # Iniciar novo servidor em background
        try:
            process = subprocess.Popen(
                ["yarn", "dev"],
                cwd=self.app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar alguns segundos para o servidor inicializar
            time.sleep(5)
            
            # Verificar se o servidor está rodando
            if process.poll() is None:
                logger.info("✅ Servidor de desenvolvimento iniciado com sucesso!")
                logger.info("🌐 Dashboard disponível em: http://localhost:3000")
                return True
            else:
                logger.error("❌ Falha ao iniciar servidor de desenvolvimento")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor: {e}")
            return False
    
    def perform_integrated_deploy(self):
        """Executa o processo completo de deploy integrado"""
        logger.info("🚀 INICIANDO DEPLOY INTEGRADO")
        start_time = time.time()
        
        try:
            # 1. Testar projeto NextJS
            if not self.test_nextjs_project():
                logger.error("❌ Falha no teste - abortando deploy")
                return False
            
            # 2. Build e checkpoint
            if not self.build_and_checkpoint():
                logger.error("❌ Falha no build/checkpoint - abortando deploy")
                return False
            
            # 3. Iniciar servidor
            if not self.start_dev_server():
                logger.warning("⚠️  Falha ao iniciar servidor, mas deploy foi concluído")
            
            # 4. Atualizar hash
            current_hash = self.calculate_file_hash(self.json_file)
            if current_hash:
                self.save_rebuild_state(current_hash)
            
            # 5. Log de sucesso
            elapsed_time = time.time() - start_time
            
            logger.info("✅ DEPLOY INTEGRADO CONCLUÍDO COM SUCESSO!")
            logger.info(f"⏱️  Tempo total: {elapsed_time:.2f} segundos")
            logger.info("🎯 Dashboard local e deployed sincronizados!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante deploy integrado: {e}")
            return False
    
    def monitor_and_deploy(self):
        """Monitora mudanças e executa deploy quando necessário"""
        logger.info("🔍 Verificando mudanças no dashboard_data.json...")
        
        if self.has_file_changed():
            logger.info("📝 Mudança detectada - iniciando deploy integrado...")
            success = self.perform_integrated_deploy()
            
            if success:
                logger.info("✅ Sistema sincronizado com sucesso!")
                return True
            else:
                logger.error("❌ Falha no deploy integrado")
                return False
        else:
            logger.info("✅ Nenhuma mudança detectada")
            return True
    
    def force_deploy(self):
        """Força um deploy independente de mudanças"""
        logger.info("🔄 DEPLOY FORÇADO INICIADO")
        return self.perform_integrated_deploy()
    
    def get_status(self):
        """Obtém status do sistema"""
        logger.info("📊 VERIFICANDO STATUS DO SISTEMA")
        
        try:
            # Verificar arquivo JSON
            if os.path.exists(self.json_file):
                json_stat = os.stat(self.json_file)
                json_size = json_stat.st_size
                json_modified = datetime.fromtimestamp(json_stat.st_mtime)
                logger.info(f"📄 JSON: {json_size} bytes, modificado em {json_modified}")
            else:
                logger.error("❌ Arquivo JSON não encontrado")
                return False
            
            # Verificar estado do rebuild
            state = self.get_rebuild_state()
            if state:
                logger.info(f"🔄 Último rebuild: {state.get('last_rebuild', 'N/A')}")
                logger.info(f"🔍 Último hash: {state.get('last_hash', 'N/A')}")
            
            # Verificar se servidor está rodando
            try:
                import requests
                response = requests.get('http://localhost:3000', timeout=5)
                if response.status_code == 200:
                    logger.info("🌐 Servidor local: ✅ ONLINE")
                else:
                    logger.info(f"🌐 Servidor local: ⚠️  Resposta {response.status_code}")
            except:
                logger.info("🌐 Servidor local: ❌ OFFLINE")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            return False

def main():
    """Função principal"""
    system = IntegratedDeploySystem()
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == '--force':
            logger.info("Modo: Deploy forçado")
            success = system.force_deploy()
        elif sys.argv[1] == '--status':
            logger.info("Modo: Verificação de status")
            success = system.get_status()
        else:
            logger.error(f"Argumento inválido: {sys.argv[1]}")
            logger.info("Uso: python3 integrated_deploy_system.py [--force|--status]")
            success = False
    else:
        logger.info("Modo: Monitoramento automático")
        success = system.monitor_and_deploy()
    
    if success:
        logger.info("🎉 Operação concluída com sucesso!")
        sys.exit(0)
    else:
        logger.error("💥 Operação falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
