
'use client';

import React, { useState, useEffect } from 'react';
import { RefreshCw, Clock, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

interface RefreshButtonProps {
  lastModified?: number;
  loadedAt?: number;
  onRefreshRequest?: () => Promise<void>;
  isLoading?: boolean;
}

export default function RefreshButton({ 
  lastModified, 
  loadedAt, 
  onRefreshRequest,
  isLoading 
}: RefreshButtonProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [wasManuallyUpdated, setWasManuallyUpdated] = useState(false);
  const [updateTimestamp, setUpdateTimestamp] = useState<number | null>(null);

  // Simple state management - no localStorage complexity
  useEffect(() => {
    if (wasManuallyUpdated) {
      const timer = setTimeout(() => {
        setWasManuallyUpdated(false);
      }, 300000); // 5 minutes
      
      return () => clearTimeout(timer);
    }
  }, [wasManuallyUpdated]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    
    // Immediately update state to show fresh data
    const now = Date.now();
    setWasManuallyUpdated(true);
    setUpdateTimestamp(now);
    
    try {
      if (onRefreshRequest) {
        // Use the dynamic data refresh function
        console.log('Refreshing dashboard data via dynamic API...');
        await onRefreshRequest();
        
        // Also call revalidate API to clear Next.js cache
        await fetch('/api/revalidate?secret=dashboard-update-2025', {
          method: 'POST',
          cache: 'no-cache'
        });
        
        console.log('Dashboard updated dynamically at:', new Date(now).toLocaleString());
        toast.success('Dashboard atualizado com sucesso!');
      } else {
        // Fallback to old method
        const response = await fetch('/api/revalidate?secret=dashboard-update-2025', {
          method: 'POST',
          cache: 'no-cache'
        });
        
        if (response.ok) {
          console.log('Dashboard updated via revalidation at:', new Date(now).toLocaleString());
          toast.success('Dashboard atualizado com sucesso!');
        } else {
          throw new Error('Falha na atualização');
        }
      }
    } catch (error) {
      toast.error('Erro ao atualizar dashboard');
      console.error('Refresh error:', error);
      
      // Reset state on error
      setWasManuallyUpdated(false);
      setUpdateTimestamp(null);
    } finally {
      setIsRefreshing(false);
    }
  };

  const getDataAge = () => {
    // If manually updated, show "Atualizado agora"
    if (wasManuallyUpdated && updateTimestamp) {
      const ageMs = Date.now() - updateTimestamp;
      const ageMinutes = Math.floor(ageMs / (1000 * 60));
      
      if (ageMinutes < 1) return 'Atualizado agora';
      if (ageMinutes < 60) return `${ageMinutes} min atrás`;
      
      const ageHours = Math.floor(ageMinutes / 60);
      if (ageHours < 24) return `${ageHours}h atrás`;
      
      const ageDays = Math.floor(ageHours / 24);
      return `${ageDays} dias atrás`;
    }
    
    // Otherwise use lastModified
    if (!lastModified) return null;
    
    const ageMs = Date.now() - lastModified;
    const ageMinutes = Math.floor(ageMs / (1000 * 60));
    
    if (ageMinutes < 1) return 'Atualizado agora';
    if (ageMinutes < 60) return `${ageMinutes} min atrás`;
    
    const ageHours = Math.floor(ageMinutes / 60);
    if (ageHours < 24) return `${ageHours}h atrás`;
    
    const ageDays = Math.floor(ageHours / 24);
    return `${ageDays} dias atrás`;
  };

  const isDataOld = () => {
    // If manually updated, data is fresh
    if (wasManuallyUpdated) {
      return false;
    }
    
    // Otherwise check if lastModified is older than 1 hour
    if (!lastModified) return false;
    
    return (Date.now() - lastModified) > 3600000;
  };

  const dataAge = getDataAge();
  const isOldData = isDataOld();

  // Debug logging
  console.log('RefreshButton state:', {
    lastModified,
    wasManuallyUpdated,
    updateTimestamp,
    dataAge,
    isOldData
  });

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Clock className="w-4 h-4" />
        <span>Atualizado: {dataAge || 'N/A'}</span>
        {isOldData && (
          <Badge variant="outline" className="text-yellow-400 border-yellow-400">
            <AlertCircle className="w-3 h-3 mr-1" />
            Dados antigos
          </Badge>
        )}
      </div>
      
      <Button
        onClick={handleRefresh}
        disabled={isRefreshing || isLoading}
        variant="outline"
        size="sm"
        className="gap-2"
      >
        <RefreshCw className={`w-4 h-4 ${(isRefreshing || isLoading) ? 'animate-spin' : ''}`} />
        {(isRefreshing || isLoading) ? 'Atualizando...' : 'Atualizar'}
      </Button>
    </div>
  );
}
