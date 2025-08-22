'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import FileUpload from '@/components/FileUpload';
import ProcessingResults from '@/components/ProcessingResults';
import ToggleControls from '@/components/ToggleControls';
import { ProcessedFile } from '@/types/document';
import { Button } from '@/components/ui/button';

export default function Home() {
  const [processedFiles, setProcessedFiles] = useState<ProcessedFile[]>([]);
  const [translateHeaders, setTranslateHeaders] = useState(false);
  const [enableValidation, setEnableValidation] = useState(true);

  const handleFileProcessed = (file: ProcessedFile) => {
    setProcessedFiles(prev => [...prev, file]);
  };

  const handleDownloadAll = () => {
    const link = document.createElement('a');
    link.href = 'http://localhost:8000/zip';
    link.download = 'processed_results.zip';
    link.click();
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar 
        processedFiles={processedFiles}
        onDownloadAll={handleDownloadAll}
      />

      <main className="flex-1 ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Document Processing
            </h1>
            <p className="text-gray-600">
              Upload PDF or image files to extract and process table data
            </p>
          </header>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            <div className="xl:col-span-2 space-y-8">
              <ToggleControls
                translateHeaders={translateHeaders}
                onTranslateHeadersChange={setTranslateHeaders}
                enableValidation={enableValidation}
                onEnableValidationChange={setEnableValidation}
              />

              <FileUpload
                onFileProcessed={handleFileProcessed}
                translateHeaders={translateHeaders}
                enableValidation={enableValidation}
              />
            </div>

            <div className="space-y-6">
              <ProcessingResults files={processedFiles} />
              <Button
                onClick={handleDownloadAll}
                className="mt-4"
              >
                Download All as ZIP
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
