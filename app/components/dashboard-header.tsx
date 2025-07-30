'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, FileText, FolderOpen, Clock } from 'lucide-react';

interface DashboardHeaderProps {
  title: string;
  totalCategorias: number;
  totalIndicacoes: number;
  dataProcessamento: string;
}

export default function DashboardHeader({ 
  title, 
  totalCategorias, 
  totalIndicacoes, 
  dataProcessamento
}: DashboardHeaderProps) {
  const [formattedDate, setFormattedDate] = useState<string>('');

  useEffect(() => {
    if (dataProcessamento) {
      try {
        // Parse the date consistently and format it
        const date = new Date(dataProcessamento + 'T00:00:00.000Z'); // Force UTC interpretation
        setFormattedDate(date.toLocaleDateString('pt-BR'));
      } catch (error) {
        setFormattedDate('N/A');
      }
    } else {
      setFormattedDate('N/A');
    }
  }, [dataProcessamento]);
  return (
    <div className="mb-8">
      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold text-white mb-2">
          {title || 'Dashboard de Indicações'}
        </h1>
        <p className="text-gray-300 text-lg">
          Análise Interativa de Indicações Municipais
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Total de Indicações</p>
              <p className="text-3xl font-bold text-white">{totalIndicacoes || 0}</p>
            </div>
            <div className="p-3 bg-blue-500/20 rounded-lg">
              <FileText className="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Categorias</p>
              <p className="text-3xl font-bold text-white">{totalCategorias || 0}</p>
            </div>
            <div className="p-3 bg-green-500/20 rounded-lg">
              <FolderOpen className="w-6 h-6 text-green-400" />
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm font-medium">Última Atualização</p>
              <p className="text-lg font-semibold text-white">
                {formattedDate || 'N/A'}
              </p>
            </div>
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <Calendar className="w-6 h-6 text-purple-400" />
            </div>
          </div>
        </div>
      </div>
      
      {/* Status automático */}
      <div className="flex justify-center mb-4">
        <div className="bg-green-500/20 border border-green-500/30 rounded-lg px-4 py-2 flex items-center gap-2">
          <Clock className="w-4 h-4 text-green-400" />
          <span className="text-green-300 text-sm font-medium">
            Sistema de monitoramento automático ativo
          </span>
        </div>
      </div>
    </div>
  );
}
