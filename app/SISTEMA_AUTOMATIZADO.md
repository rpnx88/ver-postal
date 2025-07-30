# Sistema de Monitoramento Automático de Indicações
## Câmara Municipal de Bento Gonçalves - Vereador Postal

### 🎯 **SISTEMA TOTALMENTE AUTOMATIZADO**

O sistema foi atualizado para **automação completa** - não requer mais intervenção manual!

---

## 📋 **Configuração Atual**

### **Link Monitorado:**
```
https://sapl.camarabento.rs.gov.br/materia/pesquisar-materia?tipo=8&ementa=&numero=&numeracao__numero_materia=&numero_protocolo=&ano=2025&autoria__autor=400&autoria__primeiro_autor=unknown&autoria__autor__tipo=&autoria__autor__parlamentar_set__filiacao__partido=&o=&tipo_listagem=1&tipo_origem_externa=&numero_origem_externa=&ano_origem_externa=&data_origem_externa_0=&data_origem_externa_1=&local_origem_externa=&data_apresentacao_0=&data_apresentacao_1=&data_publicacao_0=&data_publicacao_1=&relatoria__parlamentar_id=&em_tramitacao=&tramitacao__unidade_tramitacao_destino=&tramitacao__status=&materiaassunto__assunto=&indexacao=&regime_tramitacao=&salvar=Pesquisar
```

### **Parâmetros:**
- **Vereador:** Postal (ID: 400)
- **Ano:** 2025
- **Tipo:** Indicações (tipo=8)
- **Data de corte:** 22/07/2025 (apenas indicações posteriores)
- **Frequência:** A cada 30 minutos
- **Status:** ATIVO

---

## 🔄 **Fluxo Automático**

### **1. Monitoramento (A cada 30 minutos)**
- Sistema acessa o link específico do SAPL
- Busca novas indicações do Vereador Postal
- Filtra apenas indicações após 22/07/2025

### **2. Processamento Automático**
- Extrai dados: número, ementa, data, localização
- Categoriza automaticamente usando IA (8 categorias)
- Valida e processa informações

### **3. Atualização do Dashboard**
- Cria backup automático do estado atual
- Adiciona novas indicações ao `dashboard_data.json`
- Atualiza contadores e estatísticas

### **4. Rebuild Automático**
- Detecta mudanças no arquivo de dados
- Dispara rebuild do site online
- Atualiza dashboard frontend automaticamente

### **5. Logs e Auditoria**
- Salva logs detalhados de cada execução
- Mantém histórico de backups
- Registra todas as operações

---

## 📊 **Categorias Automáticas**

1. **Iluminação Pública**
2. **Sinalização e Trânsito**
3. **Pavimentação e Vias**
4. **Manutenção e Limpeza Urbana**
5. **Gestão de Resíduos**
6. **Planejamento Urbano e Programas**
7. **Espaços Públicos e Infraestrutura**
8. **Prédios Públicos**

---

## 🗂️ **Estrutura de Arquivos**

```
dashboard_indicacoes/
├── monitoring_system/
│   ├── scripts/
│   │   ├── monitor_indicacoes.py      # Script principal
│   │   ├── trigger_rebuild.py         # Trigger de rebuild
│   │   └── ...
│   ├── config/
│   │   └── system_config.json         # Configurações
│   ├── logs/                          # Logs automáticos
│   └── backups/                       # Backups automáticos
├── app/
│   ├── public/
│   │   └── dashboard_data.json        # Dados do dashboard
│   └── components/                    # Interface (sem botão refresh)
└── SISTEMA_AUTOMATIZADO.md           # Esta documentação
```

---

## 📈 **Status do Sistema**

### **✅ Implementado:**
- [x] Monitoramento automático a cada 30 minutos
- [x] Parsing do sistema SAPL específico
- [x] Categorização automática por IA
- [x] Filtro de data (apenas após 22/07/2025)
- [x] Backup automático antes de atualizações
- [x] Integração com sistema de rebuild
- [x] Logs detalhados de auditoria
- [x] Interface sem botão de atualização
- [x] Daemon task configurado e ativo

### **🎯 Resultado:**
**Sistema 100% automático** - Zero intervenção manual necessária!

---

## 🔍 **Monitoramento**

### **Logs em Tempo Real:**
```bash
# Ver logs do dia atual
tail -f /home/ubuntu/dashboard_indicacoes/monitoring_system/logs/monitor_$(date +%Y%m%d).log

# Ver último processamento
cat /home/ubuntu/dashboard_indicacoes/monitoring_system/logs/processamento_*.json | tail -1
```

### **Status do Daemon:**
- **ID:** 10f7fc035f
- **Nome:** Monitor Automático de Indicações - Vereador Postal
- **Status:** ACTIVE
- **Próxima execução:** A cada 30 minutos
- **Primeira execução:** 24/07/2025 às 03:30

---

## 🚀 **Teste Realizado**

### **Execução de Teste (24/07/2025 03:06):**
- ✅ Sistema encontrou 2 novas indicações
- ✅ IND 889/2025 - Gestão de Resíduos
- ✅ IND 884/2025 - Pavimentação e Vias
- ✅ Dashboard atualizado automaticamente
- ✅ Rebuild disparado com sucesso
- ✅ Logs salvos corretamente

---

## 🎉 **Sistema Operacional**

**O sistema está totalmente operacional e automatizado!**

### **Próximos passos automáticos:**
1. **03:30** - Primeira execução agendada
2. **04:00** - Segunda execução
3. **04:30** - Terceira execução
4. **...** - Continua a cada 30 minutos

### **Fluxo completo:**
```
Nova indicação protocolada 
    ↓
Sistema detecta (30 min)
    ↓
Atualiza dashboard_data.json
    ↓
Rebuild automático
    ↓
Site online atualizado
    ↓
Dashboard frontend sincronizado
```

**🎯 Missão cumprida: Sistema totalmente automatizado!**
