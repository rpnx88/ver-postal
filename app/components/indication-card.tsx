
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { FileText, MapPin, Calendar, Tag, Navigation, ExternalLink } from 'lucide-react';
import { IndicacaoData, extractLocationFromDescription, getStatusFromNumber, generateSaplUrl } from '@/lib/data';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface IndicationCardProps {
  indicacao: IndicacaoData;
  index: number;
}

export default function IndicationCard({ indicacao, index }: IndicationCardProps) {
  const statusInfo = getStatusFromNumber(indicacao?.numero || '');
  
  const formatDescription = (description: string) => {
    if (!description) return 'Descrição não disponível';
    return description;
  };

  const handleClick = () => {
    // Usar link direto do PDF se disponível, senão fallback para SAPL genérico
    const pdfUrl = indicacao?.pdfUrl || generateSaplUrl(indicacao?.numero || '');
    window.open(pdfUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      onClick={handleClick}
      className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 shadow-lg hover:shadow-xl hover:border-gray-600 transition-all duration-300 group cursor-pointer hover:bg-gray-800/70"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-500/20 rounded-lg group-hover:bg-blue-500/30 transition-colors">
            <FileText className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="text-white font-semibold text-lg">
              {indicacao?.numero || 'N/A'}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${statusInfo.color}`}>
                {statusInfo.status}
              </span>
            </div>
          </div>
        </div>
        
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div className="flex items-center space-x-2 opacity-60 group-hover:opacity-100 transition-opacity">
                <ExternalLink className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-gray-400 group-hover:text-blue-400 transition-colors">
                  Abrir PDF
                </span>
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-sm">
                Clique para abrir o PDF diretamente: <br />
                <strong>{indicacao?.numero || 'N/A'}</strong>
              </p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <div className="space-y-3">
        <div className="flex items-start space-x-2">
          <Navigation className="w-4 h-4 text-orange-400 mt-0.5 flex-shrink-0" />
          <p className="text-gray-300 text-sm font-medium">
            {indicacao?.rua || 'Localização não especificada'}
          </p>
        </div>

        <div className="flex items-start space-x-2">
          <Tag className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
          <p className="text-gray-300 text-sm leading-relaxed">
            {formatDescription(indicacao?.descricao || '')}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center space-x-2 text-xs text-gray-400">
          <Calendar className="w-3 h-3" />
          <span>
            Ano: {indicacao?.numero?.split?.('/')?.[1] || 'N/A'}
          </span>
        </div>
      </div>
    </motion.div>
  );
}
