
#!/usr/bin/env python3
"""
Script para atualizar os links diretos dos PDFs das indicações
Mapeia cada indicação do dashboard com seu documentoId específico do SAPL
"""

import json
import shutil
from datetime import datetime
import re

def extract_number_from_indication(numero_str):
    """Extrai o número da indicação do formato 'IND XXX/2025'"""
    if not numero_str:
        return None
    
    # Padrão para extrair o número (ex: "IND 341/2025" -> "341")
    match = re.search(r'IND\s*(\d+)/2025', numero_str.upper())
    if match:
        return int(match.group(1))
    return None

def create_backup():
    """Cria backup do dashboard_data.json atual"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data_backup_before_pdf_links_{timestamp}.json"
        
        shutil.copy2(
            "/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data.json", 
            backup_file
        )
        print(f"✅ Backup criado: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return None

def load_json_file(filepath):
    """Carrega arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar {filepath}: {e}")
        return None

def save_json_file(data, filepath):
    """Salva arquivo JSON"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar {filepath}: {e}")
        return False

def create_sapl_mapping(sapl_data):
    """Cria mapeamento de número da indicação para dados do SAPL"""
    mapping = {}
    
    for item in sapl_data:
        numero = extract_number_from_indication(item.get('numero', ''))
        if numero:
            mapping[numero] = {
                'documentoId': item.get('documentoId'),
                'pdfUrl': f"https://sapl.camarabento.rs.gov.br/documento/download/{item.get('documentoId')}",
                'ementa_completa': item.get('ementa', ''),
                'url_original': item.get('pdfUrl', '')
            }
    
    return mapping

def update_dashboard_links(dashboard_data, sapl_mapping):
    """Atualiza os links diretos no dashboard"""
    total_updated = 0
    total_not_found = 0
    updated_details = []
    not_found_details = []
    
    # Processar cada categoria no dashboard
    for categoria_nome, categoria_data in dashboard_data.get('details', {}).items():
        for indicacao in categoria_data.get('indicacoes', []):
            numero_dashboard = extract_number_from_indication(indicacao.get('numero', ''))
            
            if numero_dashboard and numero_dashboard in sapl_mapping:
                # Encontrou correspondência - atualizar URL
                old_url = indicacao.get('pdfUrl', '')
                new_url = sapl_mapping[numero_dashboard]['pdfUrl']
                
                indicacao['pdfUrl'] = new_url
                total_updated += 1
                
                updated_details.append({
                    'numero': indicacao.get('numero'),
                    'categoria': categoria_nome,
                    'old_url': old_url,
                    'new_url': new_url,
                    'documentoId': sapl_mapping[numero_dashboard]['documentoId']
                })
                
            else:
                # Não encontrou correspondência
                total_not_found += 1
                not_found_details.append({
                    'numero': indicacao.get('numero'),
                    'categoria': categoria_nome,
                    'current_url': indicacao.get('pdfUrl', '')
                })
    
    return total_updated, total_not_found, updated_details, not_found_details

def main():
    print("🔄 Iniciando atualização dos links diretos para PDFs...")
    print("=" * 60)
    
    # 1. Criar backup
    backup_file = create_backup()
    if not backup_file:
        print("❌ Falha ao criar backup - abortando operação")
        return
    
    # 2. Carregar dados do SAPL (IDs extraídos)
    print("📥 Carregando dados extraídos do SAPL...")
    sapl_data = load_json_file("/home/ubuntu/dashboard_indicacoes/sapl_document_ids.json")
    if not sapl_data:
        print("❌ Falha ao carregar dados do SAPL")
        return
    
    # 3. Carregar dados do dashboard atual
    print("📥 Carregando dados do dashboard atual...")
    dashboard_data = load_json_file("/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data.json")
    if not dashboard_data:
        print("❌ Falha ao carregar dados do dashboard")
        return
    
    # 4. Criar mapeamento
    print("🗺️  Criando mapeamento de indicações...")
    sapl_mapping = create_sapl_mapping(sapl_data)
    print(f"   📊 Total de IDs do SAPL mapeados: {len(sapl_mapping)}")
    
    # 5. Atualizar links no dashboard
    print("🔗 Atualizando links diretos...")
    total_updated, total_not_found, updated_details, not_found_details = update_dashboard_links(
        dashboard_data, sapl_mapping
    )
    
    # 6. Salvar dashboard atualizado
    print("💾 Salvando dashboard atualizado...")
    success = save_json_file(
        dashboard_data, 
        "/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data.json"
    )
    
    if not success:
        print("❌ Falha ao salvar dashboard atualizado")
        return
    
    # 7. Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DA ATUALIZAÇÃO")
    print("=" * 60)
    print(f"✅ Total de indicações atualizadas: {total_updated}")
    print(f"⚠️  Total de indicações não encontradas: {total_not_found}")
    print(f"📁 Backup salvo em: {backup_file.split('/')[-1]}")
    
    if updated_details:
        print(f"\n🔗 PRIMEIRAS 5 ATUALIZAÇÕES REALIZADAS:")
        for i, detail in enumerate(updated_details[:5]):
            print(f"   {i+1}. {detail['numero']} ({detail['categoria']})")
            print(f"      📄 DocumentoId: {detail['documentoId']}")
            print(f"      🔗 Nova URL: {detail['new_url']}")
    
    if not_found_details:
        print(f"\n⚠️  INDICAÇÕES NÃO ENCONTRADAS NO SAPL:")
        for detail in not_found_details:
            print(f"   • {detail['numero']} ({detail['categoria']})")
    
    # 8. Salvar relatório detalhado
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_updated': total_updated,
        'total_not_found': total_not_found,
        'backup_file': backup_file,
        'updated_details': updated_details,
        'not_found_details': not_found_details
    }
    
    save_json_file(report_data, "/home/ubuntu/dashboard_indicacoes/pdf_links_update_report.json")
    print(f"\n📋 Relatório detalhado salvo: pdf_links_update_report.json")
    print("\n🎉 Atualização concluída com sucesso!")

if __name__ == "__main__":
    main()
