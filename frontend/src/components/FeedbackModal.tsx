'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { getAnonymousId, track } from '@/lib/tracker';

interface FeedbackModalProps {
  page: string;
  onClose: () => void;
}

export default function FeedbackModal({ page, onClose }: FeedbackModalProps) {
  const [rating, setRating] = useState(0);
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Please select a rating');
      return;
    }
    try {
      await api.submitFeedback({
        page,
        rating,
        text: text || undefined,
        anonymous_id: getAnonymousId(),
        context: { url: window.location.href },
      });
      track('feedback_submitted', { page, rating });
      setSubmitted(true);
    } catch {
      setError('Failed to submit. Please try again.');
    }
  };

  if (submitted) {
    return (
      <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 max-w-sm w-full mx-4 text-center">
          <div className="text-3xl mb-2">&#10003;</div>
          <h3 className="text-lg font-semibold mb-1">Thank you!</h3>
          <p className="text-sm text-gray-500 mb-4">Your feedback helps us improve.</p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-sm w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Send Feedback</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>

        <p className="text-sm text-gray-500 mb-3">How was your experience on this page?</p>

        {/* Star rating */}
        <div className="flex gap-2 mb-4">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onClick={() => { setRating(star); setError(''); }}
              className={`text-2xl transition ${
                star <= rating ? 'text-yellow-400' : 'text-gray-300'
              }`}
            >
              &#9733;
            </button>
          ))}
        </div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Tell us more (optional)..."
          className="w-full border rounded-lg p-3 text-sm mb-3 resize-none"
          rows={3}
        />

        {error && <p className="text-red-500 text-xs mb-2">{error}</p>}

        <button
          onClick={handleSubmit}
          className="w-full py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition"
        >
          Submit Feedback
        </button>
      </div>
    </div>
  );
}
