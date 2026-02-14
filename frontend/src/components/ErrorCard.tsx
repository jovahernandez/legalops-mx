'use client';

import { useI18n } from '@/lib/i18n';

interface ErrorCardProps {
  message?: string;
  onRetry?: () => void;
}

export default function ErrorCard({ message, onRetry }: ErrorCardProps) {
  const { t } = useI18n();

  return (
    <div className="border border-red-200 bg-red-50 rounded-xl p-6 text-center max-w-md mx-auto">
      <div className="text-3xl mb-3">!</div>
      <p className="text-red-700 font-medium mb-2">
        {message || t('errors.fetchFailed')}
      </p>
      <p className="text-red-500 text-sm mb-4">
        {t('errors.networkError')}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition"
        >
          {t('errors.retry')}
        </button>
      )}
    </div>
  );
}
