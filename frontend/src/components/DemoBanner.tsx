'use client';

import { useI18n } from '@/lib/i18n';

export default function DemoBanner() {
  const { t } = useI18n();
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  if (!isDemoMode && apiUrl) return null;

  return (
    <div className="bg-amber-500 text-white text-center text-sm py-2 px-4 font-medium">
      {t('demo.banner')}
    </div>
  );
}
