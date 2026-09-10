import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner: React.FC<{ label?: string; size?: 'sm' | 'md' | 'lg' }> = ({ label = 'Loading...', size = 'md' }) => {
  const iconSize = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-8 h-8' : 'w-5 h-5';
  return (
    <div className="flex flex-col items-center justify-center gap-3 p-6 text-slate-400">
      <Loader2 className={`${iconSize} animate-spin text-rose-500`} />
      {label && <p className="text-xs font-mono tracking-wide">{label}</p>}
    </div>
  );
};
