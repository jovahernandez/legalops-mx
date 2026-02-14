'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import es from '@/locales/es.json';
import en from '@/locales/en.json';

export type Locale = 'es' | 'en';

const dictionaries: Record<Locale, Record<string, any>> = { es, en };

const LOCALE_KEY = 'legalops_locale';

function getNestedValue(obj: Record<string, any>, path: string): string {
  const keys = path.split('.');
  let current: any = obj;
  for (const key of keys) {
    if (current == null || typeof current !== 'object') return path;
    current = current[key];
  }
  return typeof current === 'string' ? current : path;
}

interface I18nContextType {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextType>({
  locale: 'es',
  setLocale: () => {},
  t: (key) => key,
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('es');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem(LOCALE_KEY) as Locale | null;
    if (saved && dictionaries[saved]) {
      setLocaleState(saved);
    }
    setMounted(true);
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem(LOCALE_KEY, l);
    document.documentElement.lang = l === 'es' ? 'es-MX' : 'en-US';
  }, []);

  const t = useCallback(
    (key: string): string => getNestedValue(dictionaries[locale], key),
    [locale],
  );

  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
