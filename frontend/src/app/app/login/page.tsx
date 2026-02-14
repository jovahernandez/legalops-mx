'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { useI18n } from '@/lib/i18n';

export default function LoginPage() {
  const router = useRouter();
  const { t } = useI18n();
  const [email, setEmail] = useState('admin@demo.legal');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const data = await api.login(email, password);
      localStorage.setItem('token', data.access_token);
      router.push('/app/dashboard');
    } catch (err: any) {
      if (err.message?.includes('fetch')) {
        setError(t('errors.networkError'));
      } else {
        setError(t('errors.loginFailed'));
      }
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <form onSubmit={handleLogin} className="w-full max-w-md p-8 bg-white rounded-xl shadow">
        <h1 className="text-2xl font-bold mb-6">{t('login.title')}</h1>

        {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}

        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">{t('login.emailLabel')}</label>
          <input
            type="email"
            required
            className="w-full border rounded-lg px-3 py-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-1">{t('login.passwordLabel')}</label>
          <input
            type="password"
            required
            className="w-full border rounded-lg px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-gray-800 text-white rounded-lg font-medium hover:bg-gray-900 transition"
        >
          {t('login.submitBtn')}
        </button>

        <p className="text-xs text-gray-500 mt-4 text-center">
          {t('login.demoHint')}
        </p>
      </form>
    </div>
  );
}
