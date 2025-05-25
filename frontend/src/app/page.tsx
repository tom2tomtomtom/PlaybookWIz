'use client';

import { useState } from 'react';
import {
  DocumentTextIcon,
  SparklesIcon,
  ChartBarIcon,
  LightBulbIcon,
  ArrowRightIcon,
  CloudArrowUpIcon,
  ChatBubbleLeftRightIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import Link from 'next/link';

const features = [
  {
    name: 'Document Processing',
    description: 'Upload and process PowerPoint and PDF brand playbooks with advanced AI extraction.',
    icon: DocumentTextIcon,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
  },
  {
    name: 'Intelligent Q&A',
    description: 'Ask natural language questions about your brand guidelines and get accurate answers.',
    icon: ChatBubbleLeftRightIcon,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
  },
  {
    name: 'Brand-Aligned Ideation',
    description: 'Generate creative ideas that perfectly align with your brand principles and guidelines.',
    icon: LightBulbIcon,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    href: '/ideation',
  },
  {
    name: 'Competitor Analysis',
    description: 'Analyze competitor brands and get strategic insights for positioning.',
    icon: ChartBarIcon,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
  },
  {
    name: 'Opportunity Identification',
    description: 'Discover strategic brand opportunities based on market analysis.',
    icon: EyeIcon,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-100',
  },
  {
    name: 'AI-Powered Insights',
    description: 'Leverage advanced AI to extract maximum value from your brand playbooks.',
    icon: SparklesIcon,
    color: 'text-pink-600',
    bgColor: 'bg-pink-100',
  },
];

const stats = [
  { name: 'Documents Processed', value: '10,000+' },
  { name: 'Questions Answered', value: '50,000+' },
  { name: 'Ideas Generated', value: '25,000+' },
  { name: 'Brands Analyzed', value: '1,000+' },
];

export default function HomePage() {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (files: File[]) => {
    setIsUploading(true);
    try {
      console.log('Uploading files:', files);
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="relative">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                  PlaybookWiz
                </h1>
              </div>
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

      {/* Hero Section */}
      <section className="relative px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Transform Your{' '}
              <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                Brand Playbooks
              </span>{' '}
              with AI Intelligence
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-gray-600">
              Upload your brand playbooks and unlock intelligent insights, creative ideas,
              and strategic opportunities with our advanced AI-powered platform.
            </p>

            {/* Quick Upload */}
            <div className="mx-auto mt-10 max-w-md">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-900">Upload brand playbooks</p>
                  <p className="mt-1 text-sm text-gray-600">Drag and drop files here, or click to select</p>
                  <p className="mt-1 text-xs text-gray-500">Supports PDF, PPT, PPTX (max 100MB)</p>
                </div>
              </div>
            </div>

            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link href="/dashboard" className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors">
                Get Started
                <ArrowRightIcon className="ml-2 h-4 w-4" />
              </Link>
              <Link href="/demo" className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-md hover:bg-gray-50 transition-colors">
                View Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat, index) => (
              <div key={stat.name} className="text-center">
                <div className="text-3xl font-bold text-blue-600">{stat.value}</div>
                <div className="mt-1 text-sm text-gray-600">{stat.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Powerful Features for Brand Intelligence
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
              Everything you need to unlock the full potential of your brand playbooks
            </p>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => {
              const content = (
                <>
                  <div className={`inline-flex h-12 w-12 items-center justify-center rounded-lg ${feature.bgColor}`}>
                    <feature.icon className={`h-6 w-6 ${feature.color}`} />
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-gray-900">{feature.name}</h3>
                  <p className="mt-2 text-gray-600">{feature.description}</p>
                </>
              );
              return feature.href ? (
                <Link
                  key={feature.name}
                  href={feature.href}
                  className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-6 block"
                >
                  {content}
                </Link>
              ) : (
                <div
                  key={feature.name}
                  className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow p-6"
                >
                  {content}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to Transform Your Brand Strategy?
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-lg text-blue-100">
              Join thousands of brand professionals who trust PlaybookWiz for intelligent brand analysis.
            </p>
            <div className="mt-8">
              <Link href="/auth/signup" className="inline-flex items-center px-6 py-3 bg-white text-blue-600 font-medium rounded-md hover:bg-gray-50 transition-colors">
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white">PlaybookWiz</h3>
            <p className="mt-2 text-gray-400">
              Intelligent brand playbook processing and analysis
            </p>
            <div className="mt-4 text-sm text-gray-500">
              © 2024 PlaybookWiz. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
