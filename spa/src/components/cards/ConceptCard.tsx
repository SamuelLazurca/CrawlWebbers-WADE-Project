// src/components/cards/ConceptCard.tsx
import React from 'react';
import { Link, Share2 } from 'lucide-react';
import type { Concept } from '../../types';

interface ConceptCardProps {
  concept: Concept;
  onClick?: () => void;
}

export const ConceptCard: React.FC<ConceptCardProps> = ({
  concept,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className='group relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/30 border border-slate-700/50 backdrop-blur-sm hover:shadow-xl transition-all duration-300 cursor-pointer hover:scale-105 hover:-translate-y-1'
    >
      <div
        className='absolute top-0 left-0 w-1 h-full'
        style={{ backgroundColor: concept.color }}
      />

      <div
        className='absolute top-0 right-0 w-24 h-24 opacity-10 blur-2xl rounded-full pointer-events-none'
        style={{ backgroundColor: concept.color }}
      />

      <div className='relative z-10'>
        <div className='flex items-start justify-between mb-3'>
          <div className='flex-1'>
            <div
              className='inline-block px-2 py-1 rounded text-xs font-semibold mb-2'
              style={{
                backgroundColor: `${concept.color}20`,
                color: concept.color,
              }}
            >
              {concept.category}
            </div>
            <h3 className='text-lg font-bold text-white group-hover:text-emerald-300 transition'>
              {concept.label}
            </h3>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigator.clipboard.writeText(concept.uri);
            }}
            className='p-2 rounded-lg hover:bg-slate-700/50 transition text-slate-400 hover:text-slate-200'
          >
            <Share2 size={16} />
          </button>
        </div>

        {concept.definition && (
          <p className='text-sm text-slate-300 mb-4 line-clamp-2'>
            {concept.definition}
          </p>
        )}

        {/* Footer */}
        <div className='flex items-center justify-between pt-4 border-t border-slate-700/50'>
          <div className='flex items-center gap-2 text-xs text-slate-400'>
            <Link size={14} />
            <span>{concept.relatedCount} related</span>
          </div>
          <a
            href={concept.uri}
            target='_blank'
            rel='noopener noreferrer'
            onClick={(e) => e.stopPropagation()}
            className='text-xs text-emerald-400 hover:text-emerald-300 font-medium transition'
          >
            View URI →
          </a>
        </div>
      </div>
    </div>
  );
};
