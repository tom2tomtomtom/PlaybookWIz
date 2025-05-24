'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, DocumentIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { Button } from './button';

interface FileUploadProps {
  onUpload: (files: File[]) => void;
  isUploading?: boolean;
  accept?: string;
  maxSize?: number;
  maxFiles?: number;
  className?: string;
}

export function FileUpload({
  onUpload,
  isUploading = false,
  accept = '.pdf,.ppt,.pptx',
  maxSize = 100 * 1024 * 1024, // 100MB
  maxFiles = 5,
  className,
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newFiles = [...uploadedFiles, ...acceptedFiles].slice(0, maxFiles);
      setUploadedFiles(newFiles);
    },
    [uploadedFiles, maxFiles]
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-powerpoint': ['.ppt'],
    },
    maxSize,
    maxFiles,
    disabled: isUploading,
  });

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
  };

  const handleUpload = () => {
    if (uploadedFiles.length > 0) {
      onUpload(uploadedFiles);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={cn(
          'relative cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-colors',
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400',
          isUploading && 'pointer-events-none opacity-50'
        )}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-900">
            {isDragActive ? 'Drop files here' : 'Upload brand playbooks'}
          </p>
          <p className="mt-1 text-sm text-gray-600">
            Drag and drop files here, or click to select
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Supports PDF, PPT, PPTX (max {formatFileSize(maxSize)})
          </p>
        </div>
      </div>

      {/* File Rejections */}
      {fileRejections.length > 0 && (
        <div className="mt-4 rounded-md bg-error-50 p-4">
          <h4 className="text-sm font-medium text-error-800">
            Some files were rejected:
          </h4>
          <ul className="mt-2 text-sm text-error-700">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                {file.name}: {errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900">Selected Files:</h4>
          <ul className="mt-2 space-y-2">
            {uploadedFiles.map((file, index) => (
              <li
                key={`${file.name}-${index}`}
                className="flex items-center justify-between rounded-md bg-gray-50 p-3"
              >
                <div className="flex items-center">
                  <DocumentIcon className="h-5 w-5 text-gray-400" />
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-gray-600"
                  disabled={isUploading}
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>

          {/* Upload Button */}
          <div className="mt-4">
            <Button
              onClick={handleUpload}
              disabled={isUploading || uploadedFiles.length === 0}
              className="w-full"
            >
              {isUploading ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Uploading...
                </>
              ) : (
                `Upload ${uploadedFiles.length} file${uploadedFiles.length !== 1 ? 's' : ''}`
              )}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
