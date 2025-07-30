
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell, LabelList } from 'recharts';
import { ChevronLeft, ChevronRight, ArrowLeftRight } from 'lucide-react';
import { ChartDataItem } from '@/lib/data';

interface InteractiveChartProps {
  data: ChartDataItem[];
  onCategorySelect: (category: string) => void;
  selectedCategory: string | null;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'];

export default function InteractiveChart({ data, onCategorySelect, selectedCategory }: InteractiveChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [showScrollIndicators, setShowScrollIndicators] = useState(false);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);

  // Calculate total for percentages
  const totalIndicacoes = data?.reduce((sum, item) => sum + (item?.quantidade || 0), 0) || 0;

  // Check if scroll is needed and update indicators
  const checkScrollability = () => {
    if (!chartRef.current || !isMobile) {
      setShowScrollIndicators(false);
      return;
    }

    const container = chartRef.current;
    const hasScroll = container.scrollWidth > container.clientWidth;
    setShowScrollIndicators(hasScroll);

    if (hasScroll) {
      const scrollLeft = container.scrollLeft;
      const maxScroll = container.scrollWidth - container.clientWidth;
      
      setCanScrollLeft(scrollLeft > 5);
      setCanScrollRight(scrollLeft < maxScroll - 5);
    }
  };

  // Calculate percentage for display
  const calculatePercentage = (quantidade: number) => {
    if (totalIndicacoes === 0) return '0.0';
    return ((quantidade / totalIndicacoes) * 100).toFixed(1);
  };

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    checkScrollability();
    // Add scroll event listener to update indicators
    const container = chartRef.current;
    if (container && isMobile) {
      container.addEventListener('scroll', checkScrollability);
      return () => container.removeEventListener('scroll', checkScrollability);
    }
  }, [isMobile, data]);

  const handleClick = (entry: any) => {
    if (entry?.categoria) {
      onCategorySelect(entry.categoria);
    }
  };

  // Handle clicks on the invisible overlay areas
  const handleOverlayClick = (categoria: string) => {
    onCategorySelect(categoria);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800/95 backdrop-blur-sm border border-gray-600 rounded-lg p-3 shadow-xl">
          <p className="text-white font-semibold">{label}</p>
          <p className="text-blue-400">
            Indicações: <span className="font-bold">{payload[0].value}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  // Calculate minimum width for mobile
  const getMobileWidth = () => {
    if (!isMobile || !data?.length) return '100%';
    // Each bar needs minimum width for readability (varies by category name length)
    const avgCategoryLength = data.reduce((sum, item) => sum + (item?.categoria?.length || 0), 0) / data.length;
    const minWidthPerBar = Math.max(100, Math.min(150, avgCategoryLength * 8));
    const totalMinWidth = data.length * minWidthPerBar;
    const containerWidth = chartRef.current?.clientWidth || 0;
    return Math.max(totalMinWidth, containerWidth);
  };

  // Enhanced click handler for better mobile experience
  const handleBarClick = (entry: any, index: number) => {
    if (entry?.categoria) {
      setHoveredIndex(index);
      onCategorySelect(entry.categoria);
      
      // Provide haptic feedback on mobile if available
      if (isMobile && 'vibrate' in navigator) {
        navigator.vibrate(50);
      }
    }
  };

  // Touch handlers for mobile
  const handleTouchStart = (entry: any, index: number) => {
    if (isMobile) {
      setHoveredIndex(index);
    }
  };

  const handleTouchEnd = () => {
    if (isMobile) {
      setTimeout(() => setHoveredIndex(null), 150);
    }
  };

  // Scroll functions for mobile indicators
  const scrollLeft = () => {
    if (chartRef.current) {
      chartRef.current.scrollBy({ left: -200, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (chartRef.current) {
      chartRef.current.scrollBy({ left: 200, behavior: 'smooth' });
    }
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-3 md:p-6 shadow-lg">
      <h2 className="text-xl md:text-2xl font-bold text-white mb-4 md:mb-6 text-center">
        Indicações por Categoria
      </h2>
      
      {/* Chart container with horizontal scroll on mobile */}
      <div 
        ref={chartRef}
        className={`
          relative
          ${isMobile ? 'overflow-x-auto mobile-chart-scroll mobile-chart-container' : ''}
          ${isMobile ? 'h-80' : 'h-96'}
        `}
      >
        <div 
          style={{ 
            width: isMobile ? getMobileWidth() : '100%',
            height: '100%',
            minWidth: isMobile ? getMobileWidth() : 'auto'
          }}
          className="relative"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ 
                top: 20, 
                right: isMobile ? 15 : 30, 
                left: isMobile ? 15 : 20, 
                bottom: isMobile ? 100 : 80 
              }}
              className="cursor-pointer"
              barCategoryGap={isMobile ? '15%' : '20%'}
            >
              <XAxis 
                dataKey="categoria" 
                tick={{ fontSize: isMobile ? 9 : 10, fill: '#9ca3af' }}
                tickLine={false}
                angle={-45}
                textAnchor="end"
                height={isMobile ? 100 : 80}
                interval={0}
              />
              <YAxis 
                tick={{ fontSize: isMobile ? 9 : 10, fill: '#9ca3af' }}
                tickLine={false}
                width={isMobile ? 35 : 45}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="quantidade" 
                radius={[4, 4, 0, 0]}
                onClick={(entry, index) => handleBarClick(entry, index)}
                onMouseEnter={(_, index) => !isMobile && setHoveredIndex(index)}
                onMouseLeave={() => !isMobile && setHoveredIndex(null)}
                minPointSize={isMobile ? 30 : 20} // Minimum height for better touch targets
              >
                <LabelList 
                  dataKey={(entry) => {
                    const quantidade = entry?.quantidade || 0;
                    const percentage = calculatePercentage(quantidade);
                    return `${quantidade} (${percentage}%)`;
                  }}
                  position="top" 
                  style={{ 
                    fill: '#ffffff', 
                    fontSize: isMobile ? '10px' : '11px', 
                    fontWeight: 'bold',
                    textShadow: '1px 1px 2px rgba(0,0,0,0.8)'
                  }} 
                />
                {data?.map?.((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={
                      selectedCategory === entry.categoria 
                        ? '#3b82f6' 
                        : hoveredIndex === index 
                          ? '#60a5fa' 
                          : COLORS[index % COLORS.length]
                    }
                    opacity={
                      selectedCategory && selectedCategory !== entry.categoria 
                        ? 0.4 
                        : hoveredIndex === index 
                          ? 0.8 
                          : 0.7
                    }
                    onTouchStart={() => handleTouchStart(entry, index)}
                    onTouchEnd={handleTouchEnd}
                    style={{
                      cursor: 'pointer',
                      touchAction: 'manipulation'
                    }}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>


        </div>

        {/* Mobile Scroll Indicators */}
        {isMobile && showScrollIndicators && (
          <>
            {/* Left Scroll Indicator */}
            {canScrollLeft && (
              <div className="absolute left-2 top-1/2 transform -translate-y-1/2 z-10">
                <button
                  onClick={scrollLeft}
                  className="bg-gray-900/80 backdrop-blur-sm text-white p-2 rounded-full shadow-lg border border-gray-600 hover:bg-gray-800/90 scroll-button mobile-scroll-indicator"
                  aria-label="Scroll para a esquerda"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Right Scroll Indicator */}
            {canScrollRight && (
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 z-10">
                <button
                  onClick={scrollRight}
                  className="bg-gray-900/80 backdrop-blur-sm text-white p-2 rounded-full shadow-lg border border-gray-600 hover:bg-gray-800/90 scroll-button mobile-scroll-indicator"
                  aria-label="Scroll para a direita"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Enhanced Instructions Section */}
      <div className="mt-3 md:mt-4 text-center space-y-2">
        <p className="text-gray-400 text-xs md:text-sm">
          {isMobile ? 'Toque' : 'Clique'} nas barras para visualizar os detalhes de cada categoria
        </p>
        
        {/* Enhanced Mobile Scroll Instruction */}
        {isMobile && data?.length > 4 && (
          <div className="flex items-center justify-center space-x-2">
            <ArrowLeftRight className="w-4 h-4 text-blue-400 swipe-icon" />
            <p className="text-blue-400 text-sm font-medium mobile-instruction px-3 py-1 rounded-full">
              Deslize horizontalmente para ver todas as categorias
            </p>
            <ArrowLeftRight className="w-4 h-4 text-blue-400 swipe-icon" style={{ animationDelay: '0.5s' }} />
          </div>
        )}

        {/* Mobile Scroll Dots Indicator */}
        {isMobile && showScrollIndicators && data?.length > 4 && (
          <div className="flex items-center justify-center space-x-1 mt-2 scroll-dots">
            {Array.from({ length: Math.min(data.length, 5) }).map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index < 2 && canScrollLeft
                    ? 'bg-blue-400 animate-pulse'
                    : index >= 3 && canScrollRight
                    ? 'bg-blue-400 animate-pulse'
                    : 'bg-gray-600'
                }`}
              />
            ))}
            {data?.length > 5 && (
              <span className="text-gray-500 text-xs ml-2">+{data.length - 5}</span>
            )}
          </div>
        )}

        {/* Data Summary */}
        <div className="text-gray-500 text-xs">
          <span className="font-medium text-gray-400">Total: {totalIndicacoes} indicações</span>
          {data?.length > 0 && (
            <span className="ml-2">em {data.length} categoria{data.length !== 1 ? 's' : ''}</span>
          )}
        </div>
      </div>
    </div>
  );
}
