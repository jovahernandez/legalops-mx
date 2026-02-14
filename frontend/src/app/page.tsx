'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { trackPageView, track } from '@/lib/tracker';

export default function Home() {
  useEffect(() => {
    trackPageView({ page: 'landing' });
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 bg-gradient-to-b from-white to-gray-50">
      <h1 className="text-5xl font-bold mb-4 text-center">LegalOps Agent Platform</h1>
      <p className="text-lg text-gray-600 mb-2 max-w-2xl text-center">
        Operational automation for legal teams. Intake, triage, document
        collection, and case management &mdash; powered by AI agents with
        mandatory human approval.
      </p>
      <p className="text-sm text-red-600 mb-10 max-w-lg text-center font-medium">
        This platform does NOT provide legal advice. All outputs require
        review by a licensed professional before delivery to clients.
      </p>

      {/* Dual CTA: B2B and B2C */}
      <div className="grid md:grid-cols-2 gap-8 max-w-3xl w-full">
        {/* B2B Card */}
        <div className="border rounded-xl p-8 bg-white shadow-sm hover:shadow-md transition flex flex-col items-center text-center">
          <h2 className="text-xl font-semibold mb-2">For Law Firms &amp; Legal Teams</h2>
          <p className="text-gray-500 text-sm mb-6">
            Automate intake, triage, and case operations. Onboard your firm in minutes.
          </p>
          <Link
            href="/app/onboarding/tenant"
            onClick={() => track('cta_click', { variant: 'b2b' })}
            className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition w-full"
          >
            Onboard My Firm
          </Link>
          <Link
            href="/app/login"
            className="mt-3 text-sm text-gray-500 hover:text-gray-700 transition"
          >
            Already have an account? Sign in
          </Link>
        </div>

        {/* B2C Card */}
        <div className="border rounded-xl p-8 bg-white shadow-sm hover:shadow-md transition flex flex-col items-center text-center">
          <h2 className="text-xl font-semibold mb-2">Need Legal Help?</h2>
          <p className="text-gray-500 text-sm mb-6">
            Get a free document checklist and preparation guide for your case.
            No account needed.
          </p>
          <Link
            href="/help"
            onClick={() => track('cta_click', { variant: 'b2c' })}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition w-full"
          >
            Get My Free Prep Kit
          </Link>
          <Link
            href="/intake"
            className="mt-3 text-sm text-gray-500 hover:text-gray-700 transition"
          >
            Or submit a general intake form
          </Link>
        </div>
      </div>
    </div>
  );
}
