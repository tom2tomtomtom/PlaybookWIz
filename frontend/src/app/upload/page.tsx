'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';
// import AppLayout from '@/components/layout/AppLayout';
import toast from 'react-hot-toast';

export default function UploadPage() {
  const [user, setUser] = useState<any>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [knowledgeBank, setKnowledgeBank] = useState<any[]>([]);
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'uploading' | 'processing' | 'complete' | 'error'>('idle');
  const [currentFileName, setCurrentFileName] = useState('');
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [processingDetails, setProcessingDetails] = useState<any>(null);
  const [processingSteps, setProcessingSteps] = useState<string[]>([]);
  const [uploadResults, setUploadResults] = useState<any[]>([]);
  const router = useRouter();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      router.push('/auth/signin');
      return;
    }
    setUser(JSON.parse(userData));
    loadKnowledgeBank();
  }, [router]);

  const loadKnowledgeBank = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/documents`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setKnowledgeBank(data.documents || []);
      }
    } catch (error) {
      console.error('Error loading knowledge bank:', error);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    // Check if API keys are configured
    const openaiKey = localStorage.getItem('openai_api_key');
    const claudeKey = localStorage.getItem('claude_api_key');

    if (!openaiKey && !claudeKey) {
      toast.error('Please configure your API keys first');
      router.push('/dashboard#api-keys');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setProcessingStatus('uploading');

    try {
      const results = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file) continue;

        setCurrentFileName(file.name);
        setProcessingSteps([
          `📤 Uploading ${file.name}...`,
          `🔍 Validating file format...`,
          `🧠 Processing with AI...`,
          `💾 Storing in knowledge base...`
        ]);

        const formData = new FormData();
        formData.append('file', file);

        // Get the session token
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          throw new Error('Not authenticated');
        }

        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

        setProcessingStatus('processing');
        const response = await fetch(`${backendUrl}/api/v1/documents/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          },
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to upload ${file.name}`);
        }

        const result = await response.json();
        results.push({
          ...result,
          fileName: file.name,
          fileSize: file.size,
          uploadTime: new Date().toISOString()
        });

        setUploadProgress(((i + 1) / files.length) * 100);
      }

      // Mark that user has uploaded documents
      localStorage.setItem('has_uploaded_documents', 'true');

      setProcessingStatus('complete');
      setShowSuccessModal(true);
      setFiles([]);

      // Reload knowledge bank to show new documents
      await loadKnowledgeBank();

    } catch (error) {
      console.error('Upload error:', error);
      setProcessingStatus('error');
      const errorMessage = error instanceof Error ? error.message : 'Upload failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
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
            <div className="flex items-center space-x-4">
              <Link href="/dashboard">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  PlaybookWiz
                </h1>
              </Link>
              <span className="text-gray-400">|</span>
              <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
            </div>
            <Link href="/dashboard" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Upload Area */}
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Brand Playbooks</h3>
            
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="mt-4">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Drop files here or click to upload
                  </span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    multiple
                    accept=".pdf,.ppt,.pptx"
                    className="sr-only"
                    onChange={handleFileSelect}
                  />
                </label>
                <p className="mt-1 text-sm text-gray-500">
                  Supports PDF, PPT, PPTX files up to 100MB each
                </p>
              </div>
            </div>

            {/* Selected Files */}
            {files.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Selected Files:</h4>
                <ul className="space-y-2">
                  {files.map((file, index) => (
                    <li key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div className="flex items-center">
                        <svg className="h-5 w-5 text-gray-400 mr-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm text-gray-900">{file.name}</span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </span>
                    </li>
                  ))}
                </ul>

                <div className="mt-4 flex justify-end">
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploading ? 'Uploading...' : 'Upload Files'}
                  </button>
                </div>

                {uploading && (
                  <div className="mt-4">
                    <div className="bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      Uploading... {Math.round(uploadProgress)}%
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Knowledge Bank Status */}
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">📚 Your Knowledge Bank</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${knowledgeBank.length > 0 ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                <span className="text-sm text-gray-600">
                  {knowledgeBank.length > 0 ? `${knowledgeBank.length} document${knowledgeBank.length > 1 ? 's' : ''} ready` : 'No documents yet'}
                </span>
              </div>
            </div>

            {knowledgeBank.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-gray-600 mb-2">Your knowledge bank is empty</p>
                <p className="text-sm text-gray-500">Upload brand playbooks to start asking questions</p>
              </div>
            ) : (
              <div>
                <div className="space-y-3 mb-6">
                  {knowledgeBank.map((doc, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-8 w-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-4">
                          <h4 className="text-sm font-medium text-gray-900">{doc.filename}</h4>
                          <div className="flex items-center mt-1">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              ✅ Parsed & Vectorized
                            </span>
                            <span className="ml-2 text-xs text-gray-500">
                              Ready for questions
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Call to Action */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <div className="ml-3 flex-1">
                      <h4 className="text-sm font-medium text-blue-900">Ready to ask questions!</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        Your playbooks are processed and ready. Try asking about brand guidelines, colors, messaging, or any specific topics.
                      </p>
                    </div>
                    <div className="ml-4">
                      <Link
                        href="/chat"
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                      >
                        Start Asking Questions
                        <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">🎉 Upload Complete!</h3>
              <p className="text-sm text-gray-600 mb-6">
                Your playbook has been successfully processed and added to your knowledge bank.
                You can now ask questions about your brand guidelines!
              </p>

              <div className="flex space-x-3">
                <button
                  onClick={() => setShowSuccessModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Upload More
                </button>
                <Link
                  href="/chat"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-center"
                  onClick={() => setShowSuccessModal(false)}
                >
                  Ask Questions
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Processing Modal */}
      {uploading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
                <svg className="animate-spin h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Processing Your Playbook</h3>
              <p className="text-sm text-gray-600 mb-4">
                {currentFileName && `Processing ${currentFileName}...`}
              </p>

              {processingStatus === 'uploading' && (
                <div className="text-left space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <div className="w-4 h-4 bg-blue-500 rounded-full mr-3 animate-pulse"></div>
                    📤 Uploading file...
                  </div>
                </div>
              )}

              {processingStatus === 'processing' && (
                <div className="text-left space-y-2 mb-4">
                  <div className="flex items-center text-sm text-green-600">
                    <div className="w-4 h-4 bg-green-500 rounded-full mr-3"></div>
                    ✅ File uploaded
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <div className="w-4 h-4 bg-blue-500 rounded-full mr-3 animate-pulse"></div>
                    🧠 AI is analyzing content...
                  </div>
                  <div className="flex items-center text-sm text-gray-400">
                    <div className="w-4 h-4 bg-gray-300 rounded-full mr-3"></div>
                    🔍 Creating searchable chunks...
                  </div>
                </div>
              )}

              <div className="bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>

              <p className="text-xs text-gray-500">
                This may take a few moments depending on file size...
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
