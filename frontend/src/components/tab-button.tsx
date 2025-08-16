import React from 'react';

export function TabButton({ title, isActive, onClick }: { title: string; isActive: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 font-medium text-sm rounded-t-lg border-b-2 transition-colors ${
        isActive
          ? 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400'
          : 'bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-800 dark:hover:text-gray-200'
      }`}
    >
      {title}
    </button>
  );
}
