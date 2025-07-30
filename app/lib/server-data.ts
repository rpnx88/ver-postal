
import { readFileSync } from 'fs';
import { join } from 'path';

export interface IndicacaoData {
  numero: string;
  descricao: string;
  rua: string;
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

export async function loadDashboardData(): Promise<DashboardData | null> {
  try {
    // Read file from public directory
    const filePath = join(process.cwd(), 'public', 'dashboard_data.json');
    
    // Add cache busting by checking file modification time
    const fs = require('fs');
    const stats = fs.statSync(filePath);
    const lastModified = stats.mtime.getTime();
    
    console.log(`Loading dashboard data (last modified: ${new Date(lastModified).toISOString()})`);
    
    const fileContents = readFileSync(filePath, 'utf8');
    const data: DashboardData = JSON.parse(fileContents);
    
    // Add metadata about file freshness
    const dataWithMeta = {
      ...data,
      _meta: {
        lastModified: lastModified,
        loadedAt: Date.now()
      }
    };
    
    return dataWithMeta;
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    return null;
  }
}
