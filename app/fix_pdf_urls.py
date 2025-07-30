
#!/usr/bin/env python3
import json
import re
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

def extract_indication_number(numero_str):
    """Extrai o número da indicação do formato 'IND XXX/2025'"""
    match = re.search(r'IND\s+(\d+)/(\d{4})', numero_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def format_indication_number(numero):
    """Formata o número com zeros à esquerda (ex: 418 → 00418)"""
    return f"{numero:05d}"

def extract_sapl_id_from_current_url(current_url):
    """Extrai o ID do SAPL da URL atual (formato /documento/download/{id})"""
    match = re.search(r'/documento/download/(\d+)', current_url)
    if match:
        return match.group(1)
    return None

def build_correct_pdf_url(numero, ano, sapl_id):
    """Constrói a URL correta no padrão especificado pelo usuário"""
    numero_formatado = format_indication_number(numero)
    return f"https://sapl.camarabento.rs.gov.br/media/sapl/public/materialegislativa/{ano}/{sapl_id}/cmbgind{ano}{numero_formatado}a.pdf"

def extract_ids_from_sapl_pages():
    """Extrai IDs das páginas do SAPL para construir mapeamento"""
    base_url = "https://sapl.camarabento.rs.gov.br/ta/indicacao/"
    ids_encontrados = {}
    
    print("🔍 Extraindo IDs do sistema SAPL...")
    
    # Páginas 1 e 2 como mencionado pelo usuário
    for page in [1, 2]:
        try:
            url = f"{base_url}?page={page}"
            print(f"   Processando página {page}: {url}")
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar links para indicações
                links = soup.find_all('a', href=re.compile(r'/ta/indicacao/\d+'))
                
                for link in links:
                    href = link.get('href')
                    match = re.search(r'/ta/indicacao/(\d+)', href)
                    if match:
                        sapl_id = match.group(1)
                        
                        # Tentar extrair número da indicação do texto do link
                        text = link.get_text(strip=True)
                        numero_match = re.search(r'(\d+)/2025', text)
                        if numero_match:
                            numero = int(numero_match.group(1))
                            ids_encontrados[numero] = sapl_id
                            print(f"   ✓ Indicação {numero}/2025 → ID {sapl_id}")
                        
                time.sleep(1)  # Pausa entre requisições
                
        except Exception as e:
            print(f"   ❌ Erro ao processar página {page}: {e}")
    
    return ids_encontrados

def update_dashboard_data():
    """Atualiza o dashboard_data.json com URLs corretas"""
    
    # Backup automático
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data_backup_url_fix_{timestamp}.json"
    
    # Carregar dados atuais
    with open('/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Criar backup
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"📋 Backup criado: {backup_path}")
    
    # Extrair IDs do SAPL
    sapl_ids = extract_ids_from_sapl_pages()
    
    # Atualizar URLs das indicações
    updates_count = 0
    total_indicacoes = 0
    
    # As indicações estão organizadas por categoria 
    categorias = ['Iluminação Pública', 'Sinalização e Trânsito', 'Pavimentação e Vias', 
                  'Manutenção e Limpeza Urbana', 'Gestão de Resíduos', 
                  'Planejamento Urbano e Programas', 'Espaços Públicos e Infraestrutura', 
                  'Prédios Públicos']
    
    for categoria in categorias:
        if 'details' in data and categoria in data['details'] and 'indicacoes' in data['details'][categoria]:
            print(f"\n📂 Processando categoria: {categoria}")
            for indicacao in data['details'][categoria]['indicacoes']:
                total_indicacoes += 1
                numero, ano = extract_indication_number(indicacao['numero'])
                
                if numero and ano == 2025:
                    # Primeiro, tentar usar ID do mapeamento extraído do SAPL
                    if numero in sapl_ids:
                        sapl_id = sapl_ids[numero]
                    else:
                        # Fallback: usar ID da URL atual se disponível
                        sapl_id = extract_sapl_id_from_current_url(indicacao.get('pdfUrl', ''))
                    
                    if sapl_id:
                        # Construir URL no padrão correto
                        new_url = build_correct_pdf_url(numero, ano, sapl_id)
                        old_url = indicacao.get('pdfUrl', '')
                        
                        indicacao['pdfUrl'] = new_url
                        updates_count += 1
                        
                        print(f"   ✓ {indicacao['numero']} → {new_url}")
                    else:
                        print(f"   ❌ Não foi possível encontrar ID para {indicacao['numero']}")
                else:
                    print(f"   ⚠️  Formato inválido ou ano diferente: {indicacao['numero']}")
        else:
            print(f"⚠️  Categoria '{categoria}' não encontrada ou sem indicações")
    
    # Salvar dados atualizados
    with open('/home/ubuntu/dashboard_indicacoes/app/public/dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return {
        'total_indicacoes': total_indicacoes,
        'updates_count': updates_count,
        'backup_path': backup_path,
        'sapl_ids_found': len(sapl_ids)
    }

if __name__ == "__main__":
    print("🔧 INICIANDO CORREÇÃO DE URLs DOS PDFs")
    print("="*50)
    
    resultado = update_dashboard_data()
    
    print("\n" + "="*50)
    print("📊 RESUMO DA CORREÇÃO:")
    print(f"• Total de indicações processadas: {resultado['total_indicacoes']}")
    print(f"• URLs atualizadas: {resultado['updates_count']}")
    print(f"• IDs extraídos do SAPL: {resultado['sapl_ids_found']}")
    print(f"• Backup salvo em: {resultado['backup_path']}")
    print("\n✅ CORREÇÃO CONCLUÍDA!")
