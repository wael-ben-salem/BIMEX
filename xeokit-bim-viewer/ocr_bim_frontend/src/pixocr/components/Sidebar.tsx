'use client';

import { FileText, Download, Settings, Home } from 'lucide-react';
import { ProcessedFile } from '@/types/document';

interface SidebarProps {
  processedFiles: ProcessedFile[];
  onDownloadAll: () => void;
}

export default function Sidebar({ processedFiles, onDownloadAll }: SidebarProps) {
  const completedFiles = processedFiles.filter(f => f.status === 'completed');
  const processingFiles = processedFiles.filter(f => f.status === 'processing');
  const errorFiles = processedFiles.filter(f => f.status === 'error');

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-gray-900 text-white p-6 overflow-y-auto">
      <div className="mb-8">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <FileText className="w-6 h-6" />
          DocProcessor
        </h2>
      </div>

      <nav className="space-y-2 mb-8">
        <a
          href="#"
          className="flex items-center gap-3 px-3 py-2 rounded-lg bg-blue-600 text-white"
        >
          <Home className="w-4 h-4" />
          Dashboard
        </a>
        <a
          href="#"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-gray-800 transition-colors"
        >
          <Settings className="w-4 h-4" />
          Settings
        </a>
      </nav>

      <div className="space-y-6">
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="font-semibold mb-3">File Statistics</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Completed:</span>
              <span className="text-green-400">{completedFiles.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Processing:</span>
              <span className="text-yellow-400">{processingFiles.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Errors:</span>
              <span className="text-red-400">{errorFiles.length}</span>
            </div>
          </div>
        </div>

        {completedFiles.length > 0 && (
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-semibold mb-3">Recent Files</h3>
            <div className="space-y-2">
              {completedFiles.slice(-3).map((file) => (
                <div key={file.id} className="text-sm">
                  <div className="text-gray-300 truncate" title={file.name}>
                    {file.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {file.uploadedAt.toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {completedFiles.length > 0 && (
          <button
            onClick={onDownloadAll}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            Download All
          </button>
        )}
      </div>
    </div>
  );
}