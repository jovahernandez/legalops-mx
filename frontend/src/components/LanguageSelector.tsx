'use client';

import { useI18n, Locale } from '@/lib/i18n';

export default function LanguageSelector({ className = '' }: { className?: string }) {
  const { locale, setLocale } = useI18n();

  return (
    <div className={`flex items-center gap-1 text-sm font-medium ${className}`}>
      <button
        onClick={() => setLocale('es')}
        className={`px-2 py-1 rounded transition ${
          locale === 'es'
            ? 'bg-gray-800 text-white'
            : 'text-gray-500 hover:text-gray-800'
        }`}
      >
        ES
      </button>
      <span className="text-gray-300">|</span>
      <button
        onClick={() => setLocale('en')}
        className={`px-2 py-1 rounded transition ${
          locale === 'en'
            ? 'bg-gray-800 text-white'
            : 'text-gray-500 hover:text-gray-800'
        }`}
      >
        EN
      </button>
    </div>
  );
}
