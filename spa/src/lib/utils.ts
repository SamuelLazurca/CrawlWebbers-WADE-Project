import {type ClassValue, clsx} from 'clsx';

export function cn(...inputs: ClassValue[]) {
  // If you don't want to install tailwind-merge yet, just use: return clsx(inputs);
  // But standard practice is usually:
  return clsx(inputs);
}

export const formatSize = (bytes?: number): string => {
  if (bytes === undefined || bytes === null) return '—';
  if (bytes === 0) return '0 B';

  const k = 1000;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

export const formatDate = (dateStr?: string): string => {
  if (!dateStr) return '—';
  try {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(dateStr));
  } catch {
    return 'Invalid Date';
  }
};
