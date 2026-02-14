'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/app/login');
  };

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h2 className="font-bold text-lg">LegalOps</h2>
          <p className="text-xs text-gray-400">Agent Platform</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link href="/app/dashboard" className="block px-3 py-2 rounded hover:bg-gray-800 transition">
            Dashboard
          </Link>
          <Link href="/app/pipeline" className="block px-3 py-2 rounded hover:bg-gray-800 transition">
            Pipeline
          </Link>
          <Link href="/app/approvals" className="block px-3 py-2 rounded hover:bg-gray-800 transition">
            Approvals
          </Link>
          <Link href="/app/leads" className="block px-3 py-2 rounded hover:bg-gray-800 transition">
            Leads
          </Link>
          <Link href="/app/analytics" className="block px-3 py-2 rounded hover:bg-gray-800 transition">
            Analytics
          </Link>
          <Link href="/intake" className="block px-3 py-2 rounded hover:bg-gray-800 text-blue-300 transition">
            + Nuevo Intake
          </Link>
        </nav>
        <div className="p-4 border-t border-gray-700">
          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-white transition"
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 p-6 overflow-auto">{children}</main>
    </div>
  );
}
