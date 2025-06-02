'use client';

import Link from 'next/link';

export default function DemoPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="relative">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <Link href="/">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  PlaybookWiz
                </h1>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/signin" className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                Sign In
              </Link>
              <Link href="/auth/signup" className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md">
                Get Started
              </Link>
            </div>
          </div>
        </nav>
      </header>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
            PlaybookWiz Demo
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            See how AI transforms brand playbook analysis
          </p>
        </div>

        {/* Demo Video/Screenshot Placeholder */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden mb-12">
          <div className="aspect-video bg-gray-100 flex items-center justify-center">
            <div className="text-center">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-10V7a3 3 0 01-3 3H4a3 3 0 01-3-3V4a3 3 0 013-3h16a3 3 0 013 3z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900">Interactive Demo</h3>
              <p className="text-gray-500">Watch how PlaybookWiz processes brand documents</p>
            </div>
          </div>
        </div>

        {/* Demo Features */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3 mb-12">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-medium text-gray-900">Document Upload</h3>
            </div>
            <p className="text-gray-600">
              Upload PowerPoint and PDF brand playbooks. Our AI extracts key information, brand guidelines, and visual elements.
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                PDF, PPT, PPTX
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-medium text-gray-900">Intelligent Q&A</h3>
            </div>
            <p className="text-gray-600">
              Ask natural language questions about your brand guidelines. Get instant, accurate answers based on your documents.
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Natural Language
              </span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="ml-3 text-lg font-medium text-gray-900">AI Ideation</h3>
            </div>
            <p className="text-gray-600">
              Generate creative ideas that align with your brand using AI personas. Get strategic insights and innovative concepts.
            </p>
            <div className="mt-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                AI Personas
              </span>
            </div>
          </div>
        </div>

        {/* Sample Interactions */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Sample Interactions</h2>
          
          <div className="space-y-6">
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-900">Question:</h3>
              <p className="text-gray-600">"What are our brand's primary colors and when should they be used?"</p>
              <h3 className="font-semibold text-gray-900 mt-2">AI Response:</h3>
              <p className="text-gray-600">
                "Based on your brand playbook, your primary colors are Deep Blue (#1E40AF) and Bright Orange (#F97316). 
                Deep Blue should be used for headers, primary CTAs, and professional communications. 
                Bright Orange is reserved for highlights, secondary actions, and creative elements..."
              </p>
            </div>

            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold text-gray-900">Ideation Prompt:</h3>
              <p className="text-gray-600">"Generate social media campaign ideas for our new product launch"</p>
              <h3 className="font-semibold text-gray-900 mt-2">AI Ideas:</h3>
              <ul className="text-gray-600 list-disc list-inside">
                <li>"Behind the Scenes" video series showing product development</li>
                <li>User-generated content campaign with branded hashtag</li>
                <li>Interactive polls and quizzes about product features</li>
                <li>Influencer partnerships aligned with brand values</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Try PlaybookWiz?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Start analyzing your brand playbooks with AI today
          </p>
          <div className="flex justify-center space-x-4">
            <Link
              href="/auth/signup"
              className="px-8 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
            >
              Start Free Trial
            </Link>
            <Link
              href="/"
              className="px-8 py-3 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors"
            >
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
