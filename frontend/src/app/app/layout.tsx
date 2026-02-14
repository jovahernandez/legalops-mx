'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import LanguageSelector from '@/components/LanguageSelector';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { t } = useI18n();

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/app/login');
  };

  const navItems = [
    { href: '/app/dashboard', label: t('nav.dashboard') },
    { href: '/app/pipeline', label: t('nav.pipeline') },
    { href: '/app/approvals', label: t('nav.approvals') },
    { href: '/app/leads', label: t('nav.leads') },
    { href: '/app/analytics', label: t('nav.analytics') },
  ];

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-gray-900 text-white flex flex-col shrink-0">
        <div className="p-4 border-b border-gray-700">
          <h2 className="font-bold text-lg">{t('common.appName')}</h2>
          <p className="text-xs text-gray-400">{t('common.appTagline')}</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-3 py-2 rounded transition text-sm ${
                pathname === item.href
                  ? 'bg-gray-700 text-white font-medium'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              {item.label}
            </Link>
          ))}
          <Link
            href="/intake"
            className="block px-3 py-2 rounded hover:bg-gray-800 text-blue-300 transition text-sm mt-4"
          >
            {t('nav.newIntake')}
          </Link>
        </nav>
        <div className="p-4 border-t border-gray-700 space-y-3">
          <LanguageSelector className="justify-center [&_button]:text-gray-400 [&_button]:hover:text-white [&_.bg-gray-800]:bg-gray-600" />
          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-white transition w-full text-left"
          >
            {t('nav.signOut')}
          </button>
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  );
}
