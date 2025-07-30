
export interface IndicacaoData {
  numero: string;
  descricao: string;
  rua: string;
  pdfUrl?: string;
}

export interface CategoryData {
  sheet_name: string;
  total_indicacoes: number;
  indicacoes: IndicacaoData[];
}

export interface ChartDataItem {
  categoria: string;
  quantidade: number;
  sheet_name: string;
}

export interface DashboardData {
  metadata: {
    title: string;
    total_categorias: number;
    total_indicacoes: number;
    data_processamento: string;
  };
  chart_data: ChartDataItem[];
  details: Record<string, CategoryData>;
}

export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date);
  } catch {
    return dateString;
  }
}

export function extractLocationFromDescription(description: string): string {
  const patterns = [
    /na (Rua|Avenida|Travessa|Via) ([^,]+)/i,
    /em frente ao ([^,]+)/i,
    /bairro ([^,\.]+)/i,
    /próximo ao ([^,\.]+)/i
  ];
  
  for (const pattern of patterns) {
    const match = description?.match?.(pattern);
    if (match?.[1]) {
      return match[1].trim();
    }
  }
  
  return 'Local não especificado';
}

export function getStatusFromNumber(numero: string): { status: string; color: string } {
  const year = numero?.split?.('/')?.[1];
  const currentYear = new Date().getFullYear().toString();
  
  if (year === currentYear) {
    return { status: 'Ativo', color: 'bg-green-500' };
  } else if (year && parseInt(year) < parseInt(currentYear)) {
    return { status: 'Arquivado', color: 'bg-gray-500' };
  }
  
  return { status: 'Pendente', color: 'bg-yellow-500' };
}

export function generateSaplUrl(numero: string): string {
  // DEPRECATED: Esta função não é mais necessária
  // Os links diretos agora são fornecidos através do campo pdfUrl dos dados
  // Mantida apenas para compatibilidade com código legacy
  return 'https://sapl.camarabento.rs.gov.br/';
}
