
'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, BarChart3, FileText } from 'lucide-react';
import { CategoryData } from '@/lib/data';
import IndicationCard from './indication-card';

interface DetailsPanelProps {
  selectedCategory: string | null;
  categoryData: CategoryData | null;
  onClearSelection: () => void;
}

export default function DetailsPanel({ 
  selectedCategory, 
  categoryData, 
  onClearSelection 
}: DetailsPanelProps) {
  if (!selectedCategory) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-12 shadow-lg text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="p-6 bg-gray-700/50 rounded-full w-24 h-24 flex items-center justify-center mx-auto mb-6">
            <BarChart3 className="w-10 h-10 text-gray-400" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-4">
            Bem-vindo ao Dashboard
          </h3>
          <p className="text-gray-400 text-lg max-w-md mx-auto">
            Selecione uma categoria no gráfico acima para visualizar os detalhes das indicações
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={selectedCategory}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.4 }}
        className="space-y-6"
      >
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <FileText className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">
                  {selectedCategory}
                </h2>
                <p className="text-gray-400">
                  {categoryData?.total_indicacoes || 0} indicações encontradas
                </p>
              </div>
            </div>
            
            <button
              onClick={onClearSelection}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-700/50 hover:bg-gray-700 rounded-lg transition-colors text-gray-300 hover:text-white"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Voltar</span>
            </button>
          </div>
          
          <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categoryData?.indicacoes?.map?.((indicacao, index) => (
            <IndicationCard 
              key={indicacao?.numero || index} 
              indicacao={indicacao} 
              index={index}
            />
          )) || (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-400 text-lg">
                Nenhuma indicação encontrada para esta categoria
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
