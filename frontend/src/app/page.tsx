'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { trackPageView, track } from '@/lib/tracker';
import { useI18n } from '@/lib/i18n';
import LanguageSelector from '@/components/LanguageSelector';

export default function Home() {
  const { t } = useI18n();

  useEffect(() => {
    trackPageView({ page: 'landing' });
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 md:p-8 bg-gradient-to-b from-white to-gray-50 relative">
      <div className="absolute top-4 right-4">
        <LanguageSelector />
      </div>

      <h1 className="text-4xl md:text-5xl font-bold mb-3 text-center">
        {t('common.appName')}
      </h1>
      <p className="text-base md:text-lg text-gray-600 mb-2 max-w-2xl text-center">
        {t('landing.subtitle')}
      </p>
      <p className="text-sm text-red-600 mb-10 max-w-lg text-center font-medium bg-red-50 border border-red-200 px-4 py-2 rounded-lg">
        {t('disclaimer.text')}
      </p>

      <div className="grid md:grid-cols-2 gap-6 md:gap-8 max-w-3xl w-full">
        <div className="border rounded-xl p-6 md:p-8 bg-white shadow-sm hover:shadow-md transition flex flex-col items-center text-center">
          <h2 className="text-xl font-semibold mb-2">{t('landing.b2bTitle')}</h2>
          <p className="text-gray-500 text-sm mb-6">{t('landing.b2bDesc')}</p>
          <Link
            href="/app/onboarding/tenant"
            onClick={() => track('cta_click', { variant: 'b2b' })}
            className="px-6 py-3.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition w-full font-medium text-center"
          >
            {t('landing.b2bCta')}
          </Link>
          <Link href="/app/login" className="mt-3 text-sm text-gray-500 hover:text-gray-700 transition">
            {t('landing.b2bLogin')}
          </Link>
        </div>

        <div className="border rounded-xl p-6 md:p-8 bg-white shadow-sm hover:shadow-md transition flex flex-col items-center text-center">
          <h2 className="text-xl font-semibold mb-2">{t('landing.b2cTitle')}</h2>
          <p className="text-gray-500 text-sm mb-6">{t('landing.b2cDesc')}</p>
          <Link
            href="/help"
            onClick={() => track('cta_click', { variant: 'b2c' })}
            className="px-6 py-3.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition w-full font-medium text-center"
          >
            {t('landing.b2cCta')}
          </Link>
          <Link href="/intake" className="mt-3 text-sm text-gray-500 hover:text-gray-700 transition">
            {t('landing.b2cIntake')}
          </Link>
        </div>
      </div>
    </div>
  );
}
