
#!/usr/bin/env python3
"""
Script para atualizar indicações existentes no dashboard com URLs do SAPL
"""

import json
import os

def generate_sapl_url(numero: str) -> str:
    """Gera URL do SAPL para buscar a indicação"""
    return 'https://sapl.camarabento.rs.gov.br/'

def update_dashboard_with_urls():
    """Atualiza todas as indicações existentes com URLs do SAPL"""
    dashboard_file = "/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data.json"
    
    # Carregar dados atuais
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        dashboard_data = json.load(f)
    
    # Criar backup
    backup_file = dashboard_file.replace('.json', '_backup_before_urls.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    print(f"Backup criado: {backup_file}")
    
    # Atualizar indicações em todas as categorias
    updated_count = 0
    
    for categoria_nome, categoria_data in dashboard_data.get('details', {}).items():
        for indicacao in categoria_data.get('indicacoes', []):
            # Verificar se já tem pdfUrl
            if 'pdfUrl' not in indicacao:
                indicacao['pdfUrl'] = generate_sapl_url(indicacao.get('numero', ''))
                updated_count += 1
    
    # Salvar dados atualizados
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dashboard atualizado!")
    print(f"📊 Total de indicações atualizadas: {updated_count}")
    print(f"🔗 Todas as indicações agora têm links para o SAPL")
    
    return updated_count

if __name__ == "__main__":
    try:
        count = update_dashboard_with_urls()
        print(f"\n🎉 Atualização concluída com sucesso! {count} indicações foram atualizadas.")
    except Exception as e:
        print(f"❌ Erro durante atualização: {e}")
