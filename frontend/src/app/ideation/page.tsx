'use client';

import { useState } from 'react';
import Link from 'next/link';

const personas = [
  { id: 'aiden', name: 'Aiden', description: 'Strategic Brand Visionary' },
  { id: 'maya', name: 'Maya', description: 'Creative Innovation Catalyst' },
  { id: 'leo', name: 'Leo', description: 'Data-Driven Strategist' },
  { id: 'zara', name: 'Zara', description: 'Disruptive Innovation Expert' },
];

export default function IdeationPage() {
  const [prompt, setPrompt] = useState('');
  const [selectedPersona, setSelectedPersona] = useState('aiden');
  const [ideas, setIdeas] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const generateIdeas = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/ideation/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_ids: [],
          prompt,
          use_personas: true,
          personas: [selectedPersona],
        }),
      });
      if (!res.ok) {
        throw new Error('Failed to generate ideas');
      }
      const data = await res.json();
      setIdeas(data.ideas || []);
    } catch (err) {
      console.error(err);
      alert('Error generating ideas');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Persona-Based Ideation</h1>
      <p className="mb-4 text-gray-600">
        Select a creative persona and provide a prompt to generate brand-aligned ideas using our AI service.
      </p>
      <div className="mb-4">
        <label htmlFor="persona" className="block mb-1 font-medium">
          Persona
        </label>
        <select
          id="persona"
          value={selectedPersona}
          onChange={e => setSelectedPersona(e.target.value)}
          className="w-full border rounded p-2"
        >
          {personas.map(p => (
            <option key={p.id} value={p.id}>
              {p.name} - {p.description}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-4">
        <label htmlFor="prompt" className="block mb-1 font-medium">
          Ideation Prompt
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          className="w-full border rounded p-2 h-24"
        />
      </div>
      <button
        onClick={generateIdeas}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Generating...' : 'Generate Ideas'}
      </button>
      {ideas.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Ideas</h2>
          <ul className="list-disc list-inside space-y-2">
            {ideas.map((idea, idx) => (
              <li key={idx}>{idea.title || idea}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="mt-8">
        <Link href="/" className="text-blue-600 hover:underline">
          Back to Home
        </Link>
      </div>
    </div>
  );
}
