'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';
// import AppLayout from '@/components/layout/AppLayout';
// import OnboardingFlow from '@/components/onboarding/OnboardingFlow';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [openaiKey, setOpenaiKey] = useState('');
  const [claudeKey, setClaudeKey] = useState('');
  const [showKeys, setShowKeys] = useState(false);
  const [keysSaved, setKeysSaved] = useState(false);
  // const [showOnboarding, setShowOnboarding] = useState(false);
  // const [isFirstVisit, setIsFirstVisit] = useState(false);
  const [systemStats, setSystemStats] = useState({
    documentsCount: 0,
    chatSessions: 0,
    lastActivity: null as string | null,
  });
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/auth/signin');
        return;
      }
      setUser(user);

      // Check if first visit
      // const hasVisited = localStorage.getItem('has_visited_dashboard');
      // if (!hasVisited) {
      //   setIsFirstVisit(true);
      //   setShowOnboarding(true);
      //   localStorage.setItem('has_visited_dashboard', 'true');
      // }

      // Load saved API keys
      const savedOpenAI = localStorage.getItem('openai_api_key');
      const savedClaude = localStorage.getItem('claude_api_key');
      if (savedOpenAI) setOpenaiKey(savedOpenAI);
      if (savedClaude) setClaudeKey(savedClaude);

      // Load system stats
      await loadSystemStats();
    };

    checkUser();
  }, [router]);

  const loadSystemStats = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/stats`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });

      if (response.ok) {
        const stats = await response.json();
        setSystemStats({
          documentsCount: stats.documents_uploaded || 0,
          chatSessions: stats.chat_sessions || 0,
          lastActivity: stats.last_activity || new Date().toISOString(),
        });
      }
    } catch (error) {
      console.error('Error loading system stats:', error);
    }
  };

  const handleSaveKeys = async () => {
    if (!openaiKey.trim() && !claudeKey.trim()) {
      toast.error('Please enter at least one API key');
      return;
    }

    const loadingToast = toast.loading('Saving API keys...');

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        toast.error('Please sign in to save API keys');
        return;
      }

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

      if (openaiKey.trim()) {
        const response = await fetch(`${backendUrl}/api/v1/auth/api-keys`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify({
            provider: 'openai',
            api_key: openaiKey.trim()
          })
        });

        if (!response.ok) {
          throw new Error('Failed to save OpenAI API key');
        }

        localStorage.setItem('openai_api_key', openaiKey.trim());
      }

      if (claudeKey.trim()) {
        const response = await fetch(`${backendUrl}/api/v1/auth/api-keys`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify({
            provider: 'claude',
            api_key: claudeKey.trim()
          })
        });

        if (!response.ok) {
          throw new Error('Failed to save Claude API key');
        }

        localStorage.setItem('claude_api_key', claudeKey.trim());
      }

      toast.dismiss(loadingToast);
      toast.success('API keys saved successfully!');
      setKeysSaved(true);
      setTimeout(() => setKeysSaved(false), 3000);
    } catch (error) {
      toast.dismiss(loadingToast);
      console.error('Error saving API keys:', error);
      toast.error('Failed to save API keys. Please try again.');
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link href="/">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  PlaybookWiz
                </h1>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user.email?.split('@')[0] || user.email}</span>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {/* API Key Configuration */}
        <div id="api-keys" className="bg-white overflow-hidden shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  AI Provider Configuration
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Configure your AI provider API keys to enable intelligent document processing and Q&A.
                </p>
              </div>
              <div className="flex items-center space-x-2">
                {(openaiKey || claudeKey) && (
                  <div className="flex items-center text-green-600">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm">Configured</span>
                  </div>
                )}
              </div>
            </div>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="openai-key" className="block text-sm font-medium text-gray-700">
                    OpenAI API Key
                  </label>
                  <div className="mt-1 relative">
                    <input
                      type={showKeys ? 'text' : 'password'}
                      id="openai-key"
                      value={openaiKey}
                      onChange={(e) => setOpenaiKey(e.target.value)}
                      placeholder="sk-..."
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="claude-key" className="block text-sm font-medium text-gray-700">
                    Claude API Key (Anthropic)
                  </label>
                  <div className="mt-1 relative">
                    <input
                      type={showKeys ? 'text' : 'password'}
                      id="claude-key"
                      value={claudeKey}
                      onChange={(e) => setClaudeKey(e.target.value)}
                      placeholder="sk-ant-..."
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="show-keys"
                      type="checkbox"
                      checked={showKeys}
                      onChange={(e) => setShowKeys(e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="show-keys" className="ml-2 block text-sm text-gray-900">
                      Show API keys
                    </label>
                  </div>

                  <button
                    onClick={handleSaveKeys}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    Save Keys
                  </button>
                </div>

                {keysSaved && (
                  <div className="text-green-600 text-sm">
                    ✓ API keys saved successfully!
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Link href="/upload" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Upload Documents</dt>
                      <dd className="text-lg font-medium text-gray-900">Upload Playbooks</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </Link>

            <Link href="/ideation" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">AI Ideation</dt>
                      <dd className="text-lg font-medium text-gray-900">Generate Ideas</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </Link>

            <Link href="/chat" className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Q&A Chat</dt>
                      <dd className="text-lg font-medium text-gray-900">Ask Questions</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
