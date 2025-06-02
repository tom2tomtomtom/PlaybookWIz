'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';

interface Source {
  passage: string;
  document_name: string;
  page_number: number;
  relevance_score: number;
  document_id: string;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  sources?: Source[];
  processing_time?: number;
  provider_used?: string;
}

export default function ChatPage() {
  const [user, setUser] = useState<any>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated with Supabase
    const checkUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/auth/signin');
        return;
      }
      setUser(user);

      // Add welcome message
      setMessages([{
        id: '1',
        type: 'assistant',
        content: 'Hello! I\'m your intelligent brand playbook assistant. I can analyze your uploaded documents and provide answers with source attribution and confidence scores. Ask me anything about your brand guidelines!',
        timestamp: new Date(),
        confidence: 1.0,
        sources: []
      }]);

      // Load user's documents
      const loadDocuments = async () => {
        try {
          const { data: { session } } = await supabase.auth.getSession();
          if (session) {
            const response = await fetch('http://localhost:8000/api/v1/documents', {
              headers: {
                'Authorization': `Bearer ${session.access_token}`
              }
            });
            if (response.ok) {
              const data = await response.json();
              setDocuments(data.documents || []);
            }
          }
        } catch (error) {
          console.error('Error loading documents:', error);
        }
      };

      loadDocuments();
    };

    checkUser();
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Get the session token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        throw new Error('Not authenticated');
      }

      const response = await fetch('http://localhost:8000/api/v1/chat/intelligent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          document_ids: [], // You can add document selection later
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.response || 'I apologize, but I couldn\'t generate a response. Please try again.',
        timestamp: new Date(),
        confidence: data.confidence || 0,
        sources: data.sources || [],
        processing_time: data.processing_time || 0,
        provider_used: data.provider_used || 'unknown'
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Something went wrong. Please check your API keys and try again.'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  PlaybookWiz
                </h1>
              </Link>
              <span className="text-gray-400">|</span>
              <h2 className="text-xl font-semibold text-gray-900">AI Chat</h2>
            </div>
            <Link href="/dashboard" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 max-w-4xl mx-auto w-full py-6 px-4 sm:px-6 lg:px-8 flex flex-col">
        {/* Messages */}
        <div className="flex-1 bg-white rounded-lg shadow overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-2xl px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  {/* AI Response Metadata */}
                  {message.type === 'assistant' && message.confidence !== undefined && (
                    <div className="mt-3 pt-2 border-t border-gray-200">
                      {/* Confidence Score */}
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-gray-600">Confidence:</span>
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className={`h-2 rounded-full ${
                                message.confidence > 0.8 ? 'bg-green-500' :
                                message.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${message.confidence * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-600">
                            {Math.round(message.confidence * 100)}%
                          </span>
                        </div>
                      </div>

                      {/* Processing Info */}
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                        <span>Provider: {message.provider_used}</span>
                        <span>{message.processing_time?.toFixed(2)}s</span>
                      </div>

                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-600 mb-1">Sources:</p>
                          <div className="space-y-1">
                            {message.sources.slice(0, 3).map((source, index) => (
                              <div key={index} className="text-xs bg-white p-2 rounded border">
                                <div className="flex justify-between items-start mb-1">
                                  <span className="font-medium text-blue-600">
                                    {source.document_name}
                                  </span>
                                  <span className="text-gray-500">
                                    Page {source.page_number} • {Math.round(source.relevance_score * 100)}%
                                  </span>
                                </div>
                                <p className="text-gray-700 line-clamp-2">
                                  {source.passage.substring(0, 100)}...
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <p className={`text-xs mt-2 ${
                    message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-500">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask intelligent questions about your brand playbooks..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </form>
            <p className="text-xs text-gray-500 mt-2">
              Get intelligent answers with source attribution and confidence scores. I'll search your uploaded brand playbooks and provide accurate, verifiable responses.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
