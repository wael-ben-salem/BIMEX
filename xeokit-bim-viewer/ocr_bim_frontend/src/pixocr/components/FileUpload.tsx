'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File as FileIcon, X, Loader2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ProcessedFile, FileUploadProps } from '@/types/document';

// Belt & suspenders: use env var OR fall back to FastAPI localhost.
// Also strip any trailing slash to avoid '//' in URLs.
const API_BASE = (process.env.NEXT_PUBLIC_API || 'http://127.0.0.1:8001').replace(/\/$/, '');

export default function FileUpload({
  onFileProcessed,
  translateHeaders,
  enableValidation,
  generatePdf = true,
}: FileUploadProps & { generatePdf?: boolean }) {
  const [uploadingFiles, setUploadingFiles] = useState<ProcessedFile[]>([]);

  const processFile = async (file: File) => {
    const fileId = `${file.name}-${Date.now()}`;
    const processedFile: ProcessedFile = {
      id: fileId,
      name: file.name,
      originalFile: file,
      status: 'uploading',
      uploadedAt: new Date(),
    };

    setUploadingFiles(prev => [...prev, processedFile]);

    try {
      setUploadingFiles(prev =>
        prev.map(f => (f.id === fileId ? { ...f, status: 'processing' } : f))
      );

      const formData = new FormData();
      formData.append('file', file);

      const qs = new URLSearchParams({
        translate_headers: String(!!translateHeaders),
        validate_schema: String(!!enableValidation),
        generate_pdf: String(!!generatePdf),
      });

      const url = `${API_BASE}/pixocr/process?${qs.toString()}`;
      // Helpful breadcrumb in DevTools
      console.log('[Upload] API_BASE =', API_BASE);
      console.log('[Upload] POST', url);

      const res = await fetch(url, {
        method: 'POST',
        body: formData,
        // reduce weird dev caching/proxy issues
        cache: 'no-store',
        credentials: 'omit',
      });

      const contentType = res.headers.get('content-type') || '';
      console.log('[Upload] Response', res.status, contentType);

      // If the request accidentally hit Next.js, you'll get an HTML page.
      if (contentType.includes('text/html')) {
        const htmlSnippet = (await res.text().catch(() => '')).slice(0, 200);
        throw new Error(
          'Received HTML instead of JSON from /process. ' +
          'This means the request hit the Next.js dev server. ' +
          'Ensure NEXT_PUBLIC_API points to FastAPI (e.g., http://127.0.0.1:8001). ' +
          `Snippet: ${htmlSnippet}`
        );
      }

      if (!res.ok) {
        const msg = await res.text().catch(() => res.statusText);
        throw new Error(msg || `HTTP ${res.status}`);
      }

      // Safe to parse JSON
      const results = await res.json();

      const completedFile: ProcessedFile = {
        ...processedFile,
        status: 'completed',
        results,
      };

      setUploadingFiles(prev => prev.filter(f => f.id !== fileId));
      onFileProcessed(completedFile);
    } catch (err: any) {
      const message = err?.message || 'Failed to process file';
      console.error('[Upload] Error:', message);

      const errorFile: ProcessedFile = {
        ...processedFile,
        status: 'error',
        error: message,
      };
      setUploadingFiles(prev =>
        prev.map(f => (f.id === fileId ? errorFile : f))
      );
    }
  };

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach(processFile);
    },
    [translateHeaders, enableValidation, generatePdf]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
    },
    multiple: true,
  });

  const removeUploadingFile = (fileId: string) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <div className="space-y-6">
      <Card className="p-8">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          {isDragActive ? (
            <p className="text-blue-600 text-lg">Drop the files here...</p>
          ) : (
            <div>
              <p className="text-gray-700 text-lg mb-2">
                Drag & drop files here, or click to select
              </p>
              <p className="text-gray-500 text-sm">
                Supports PDF and image files (PNG, JPG, GIF, BMP)
              </p>
            </div>
          )}
        </div>
      </Card>

      {uploadingFiles.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Processing Files</h3>
          <div className="space-y-4">
            {uploadingFiles.map(file => (
              <div key={file.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <FileIcon className="w-5 h-5 text-gray-500" />
                    <span className="font-medium truncate" title={file.name}>
                      {file.name}
                    </span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => file.id && removeUploadingFile(file.id)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="flex items-center gap-3">
                  {file.status === 'uploading' && (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      <span className="text-sm text-gray-600">Uploading...</span>
                    </>
                  )}
                  {file.status === 'processing' && (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-orange-600" />
                      <span className="text-sm text-gray-600">Processing...</span>
                    </>
                  )}
                  {file.status === 'error' && (
                    <span className="text-sm text-red-600">
                      Error: {file.error}
                    </span>
                  )}
                </div>

                {(file.status === 'uploading' || file.status === 'processing') && (
                  <Progress
                    value={file.status === 'uploading' ? 30 : 70}
                    className="mt-2"
                  />
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
