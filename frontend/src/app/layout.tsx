import type { Metadata } from 'next';
import './globals.css';
import { I18nProvider } from '@/lib/i18n';
import DemoBanner from '@/components/DemoBanner';

export const metadata: Metadata = {
  title: 'LegalOps \u2014 Plataforma de Operaciones Legales',
  description: 'Plataforma multi-tenant de operaciones legales. Automatiza intake, documentos y gesti\u00f3n de casos.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-MX">
      <body className="min-h-screen">
        <I18nProvider>
          <DemoBanner />
          {children}
        </I18nProvider>
      </body>
    </html>
  );
}
