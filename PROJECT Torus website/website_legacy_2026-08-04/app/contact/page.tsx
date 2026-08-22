'use client';

import { useState } from 'react';

export default function ContactPage() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError('');

    const form = e.currentTarget;
    const formData = new FormData(form);
    
    // Build payload for Formspree
    const payload = {
      name: String(formData.get('name') || '').trim(),
      email: String(formData.get('email') || '').trim(),
      message: String(formData.get('message') || '').trim(),
      _subject: `Torus Coffee Contact: ${String(formData.get('name') || '').trim()}`,
    };

    try {
      const response = await fetch('https://formspree.io/f/moeaaqbk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      
      if (response.ok && !data.error) {
        setSent(true);
        form.reset();
      } else {
        setError(data.error || 'Something went wrong. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please try again later.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="bg-white">
      <section className="border-b border-gray-200">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900">Contact</h1>
          <p className="mt-4 text-lg text-gray-600">
            Wholesale, vendor, or general questions.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-12">
        {sent ? (
          <div className="rounded-lg border border-green-200 bg-green-50 p-6 text-green-800">
            Message sent. We will get back to you.
          </div>
        ) : (
          <form onSubmit={onSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                name="name"
                required
                className="mt-1 w-full rounded-lg border border-gray-300 p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                name="email"
                required
                className="mt-1 w-full rounded-lg border border-gray-300 p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Message</label>
              <textarea
                name="message"
                required
                rows={5}
                className="mt-1 w-full rounded-lg border border-gray-300 p-2"
              />
            </div>
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-gray-900 px-5 py-3 text-white hover:bg-gray-800 disabled:opacity-60"
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
        )}
      </section>
    </main>
  );
}
