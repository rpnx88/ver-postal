
'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Search, X, AlertCircle } from 'lucide-react';
import { DashboardData, ChartDataItem, IndicacaoData, CategoryData } from '@/lib/data';
import { useDashboardData } from '@/hooks/use-dashboard-data';
import { toast } from 'sonner';
import DashboardHeader from './dashboard-header';
import InteractiveChart from './interactive-chart';
import DetailsPanel from './details-panel';

interface DashboardClientProps {
  initialData: DashboardData;
}

export default function DashboardClient({ initialData }: DashboardClientProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  // Use dynamic data hook
  const { data, loading, error, lastFetch, refetch } = useDashboardData(initialData);

  // Show error state if data fails to load
  useEffect(() => {
    if (error) {
      toast.error(`Erro ao carregar dados: ${error}`);
    }
  }, [error]);

  // Handle data refresh from external sources (like RefreshButton)
  useEffect(() => {
    const handleRefreshData = () => {
      console.log('External refresh request detected');
      refetch();
    };

    // Listen for custom refresh events
    window.addEventListener('dashboard-refresh', handleRefreshData);
    
    return () => {
      window.removeEventListener('dashboard-refresh', handleRefreshData);
    };
  }, [refetch]);

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) {
      return data;
    }

    const searchLower = searchTerm.toLowerCase().trim();
    
    // Filter details by searching in number, description, and location
    const filteredDetails: { [key: string]: CategoryData } = {};
    const categoryCounts: { [key: string]: number } = {};

    Object.entries(data?.details || {}).forEach(([category, categoryData]) => {
      const filtered = categoryData?.indicacoes?.filter((indicacao) => {
        const numero = indicacao?.numero?.toLowerCase() || '';
        const descricao = indicacao?.descricao?.toLowerCase() || '';
        const rua = indicacao?.rua?.toLowerCase() || '';
        
        return numero.includes(searchLower) || 
               descricao.includes(searchLower) || 
               rua.includes(searchLower);
      }) || [];

      if (filtered.length > 0) {
        filteredDetails[category] = {
          ...categoryData,
          indicacoes: filtered,
          total_indicacoes: filtered.length
        };
        categoryCounts[category] = filtered.length;
      }
    });

    // Create filtered chart data
    const filteredChartData: ChartDataItem[] = Object.entries(categoryCounts).map(([categoria, quantidade]) => {
      const originalData = data?.chart_data?.find(item => item.categoria === categoria);
      return {
        categoria,
        quantidade,
        sheet_name: originalData?.sheet_name || ''
      };
    });

    // Calculate new metadata
    const totalIndicacoes = Object.values(categoryCounts).reduce((sum, count) => sum + count, 0);
    const totalCategorias = Object.keys(categoryCounts).length;

    return {
      ...data,
      chart_data: filteredChartData,
      details: filteredDetails,
      metadata: {
        ...data?.metadata,
        total_indicacoes: totalIndicacoes,
        total_categorias: totalCategorias
      }
    };
  }, [data, searchTerm]);

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    // Scroll to details panel smoothly
    setTimeout(() => {
      const detailsElement = document.getElementById('details-panel');
      if (detailsElement) {
        detailsElement.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }
    }, 100);
  };

  const handleClearSelection = () => {
    setSelectedCategory(null);
  };

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    // Clear selection when search changes
    if (selectedCategory && value.trim()) {
      setSelectedCategory(null);
    }
  };

  const handleClearSearch = () => {
    setSearchTerm('');
    setSelectedCategory(null);
  };

  const selectedCategoryData = selectedCategory ? (filteredData?.details?.[selectedCategory] || null) : null;

  // Loading state
  if (!data && loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-white mb-2">Carregando Dashboard</h2>
          <p className="text-gray-400">Aguarde enquanto carregamos os dados...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Erro ao Carregar</h2>
          <p className="text-gray-400 mb-4">Não foi possível carregar os dados do dashboard.</p>
          <button
            onClick={refetch}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={false}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <DashboardHeader
            title={filteredData?.metadata?.title || 'Dashboard de Indicações'}
            totalCategorias={filteredData?.metadata?.total_categorias || 0}
            totalIndicacoes={filteredData?.metadata?.total_indicacoes || 0}
            dataProcessamento={filteredData?.metadata?.data_processamento || ''}
          />
        </motion.div>

        {/* Search Component */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mt-6"
        >
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-4 shadow-lg">
            <div className="flex items-center space-x-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  placeholder="Buscar por número, descrição ou rua..."
                  className="w-full pl-10 pr-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
                {searchTerm && (
                  <button
                    onClick={handleClearSearch}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-600 rounded-full transition-colors duration-200"
                  >
                    <X className="w-4 h-4 text-gray-400 hover:text-white" />
                  </button>
                )}
              </div>
            </div>
            
            {searchTerm && (
              <div className="mt-3 flex items-center justify-between text-sm">
                <span className="text-gray-300">
                  {filteredData?.metadata?.total_indicacoes === 0 ? (
                    'Nenhum resultado encontrado'
                  ) : (
                    `${filteredData?.metadata?.total_indicacoes || 0} resultado${(filteredData?.metadata?.total_indicacoes || 0) !== 1 ? 's' : ''} encontrado${(filteredData?.metadata?.total_indicacoes || 0) !== 1 ? 's' : ''}`
                  )}
                </span>
                <button
                  onClick={handleClearSearch}
                  className="text-blue-400 hover:text-blue-300 font-medium transition-colors duration-200"
                >
                  Limpar busca
                </button>
              </div>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <InteractiveChart
            data={filteredData?.chart_data || []}
            onCategorySelect={handleCategorySelect}
            selectedCategory={selectedCategory}
          />
        </motion.div>

        <motion.div
          id="details-panel"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-8"
        >
          <DetailsPanel
            selectedCategory={selectedCategory}
            categoryData={selectedCategoryData}
            onClearSelection={handleClearSelection}
          />
        </motion.div>
      </div>
    </div>
  );
}
