'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Download,
  Image as ImageIcon,
  Table as TableIcon,
  FileText,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';
import { ProcessingResultsProps } from '@/types/document';

const API_BASE = process.env.NEXT_PUBLIC_API || '';

export default function ProcessingResults({ files }: ProcessingResultsProps) {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [tablesData, setTablesData] = useState<string[][][]>([]);
  const [headerJson, setHeaderJson] = useState<any>(null);

  const completedFiles = files.filter(f => f.status === 'completed');
  const activeFile = selectedFile
    ? completedFiles.find(f => f.id === selectedFile)
    : completedFiles[completedFiles.length - 1];

  // fetch table CSVs and parse
  useEffect(() => {
    const fetchTables = async () => {
      setTablesData([]);
      if (!activeFile?.results?.table_csvs) return;

      const csvPaths = (activeFile.results.table_csvs || []).filter(Boolean) as string[];
      const tables: string[][][] = await Promise.all(
        csvPaths.map(async (csvPath: string) => {
          try {
            const res = await fetch(`${API_BASE}${csvPath}`);
            const text = await res.text();
            // very simple CSV split; good enough for our data (no quoted commas)
            const rows = text.trim().split('\n').map(r => r.split(','));
            return rows;
          } catch (err) {
            console.error('Failed to load CSV:', csvPath, err);
            return [];
          }
        })
      );
      setTablesData(tables);
    };
    fetchTables();
  }, [activeFile]);

  // fetch and display the header JSON (previously the UI showed the path)
  useEffect(() => {
    const fetchHeader = async () => {
      setHeaderJson(null);
      const p = activeFile?.results?.header_json;
      if (!p) return;
      try {
        const res = await fetch(`${API_BASE}${p}`);
        const data = await res.json();
        setHeaderJson(data);
      } catch (e) {
        console.warn('Failed to load header JSON:', p);
      }
    };
    fetchHeader();
  }, [activeFile]);

  const downloadFileFromURL = async (url: string, filename: string) => {
    const response = await fetch(`${API_BASE}${url}`);
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  if (completedFiles.length === 0) {
    return (
      <Card className="p-8 text-center">
        <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-700 mb-2">
          No Results Yet
        </h3>
        <p className="text-gray-500">
          Upload and process files to see results here
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Processed Files</h3>
        <div className="space-y-2">
          {completedFiles.map(file => (
            <div
              key={file.id ?? file.name}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                selectedFile === file.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedFile(file.id ?? null)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-sm font-medium truncate" title={file.name}>
                    {file.name}
                  </span>
                </div>
                <Badge variant="secondary" className="text-xs">
                  {file.results?.warnings?.length || 0} warnings
                </Badge>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {file.uploadedAt ? file.uploadedAt.toLocaleString() : 'Date unknown'}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {activeFile?.results && (() => {
        const results = activeFile.results;
        const csv0 = results.table_csvs?.[0];

        return (
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Results: {activeFile.name}</h3>
              <div className="flex gap-2 flex-wrap">
                {csv0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => downloadFileFromURL(csv0, `${activeFile.name}.csv`)}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    CSV
                  </Button>
                )}
                {results.full_text_json && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      downloadFileFromURL(results.full_text_json, `${activeFile.name}.json`)
                    }
                  >
                    <Download className="w-4 h-4 mr-2" />
                    JSON
                  </Button>
                )}
                {results.report_pdf && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(`${API_BASE}${results.report_pdf}`, '_blank')}
                  >
                    📄 Download PDF
                  </Button>
                )}
                {results.llm_review_txt && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(`${API_BASE}${results.llm_review_txt}`, '_blank')}
                  >
                    🤖 LLM Review
                  </Button>
                )}
              </div>
            </div>

            {results.report_pdf && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">📄 PDF Preview</h4>
                <iframe
                  src={`${API_BASE}${results.report_pdf}`}
                  width="100%"
                  height="600px"
                  className="border rounded-lg"
                  title="PDF Preview"
                />
              </div>
            )}

            <Tabs defaultValue="table" className="space-y-4 mt-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="table" className="flex items-center gap-2">
                  <TableIcon className="w-4 h-4" />
                  Table
                </TabsTrigger>
                <TabsTrigger value="images" className="flex items-center gap-2">
                  <ImageIcon className="w-4 h-4" />
                  Images
                </TabsTrigger>
                <TabsTrigger value="metadata" className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Metadata
                </TabsTrigger>
                <TabsTrigger value="warnings" className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Warnings
                </TabsTrigger>
              </TabsList>

              {/* TABLES TAB */}
              <TabsContent value="table" className="space-y-4">
                {tablesData.length ? (
                  tablesData.map((table, index) => {
                    const [headers = [], ...rows] = table || [];
                    const perTableCsv = results.table_csvs?.[index];

                    return (
                      <div key={index} className="border rounded-lg overflow-hidden">
                        <div className="bg-gray-50 px-4 py-2 flex items-center justify-between">
                          <h4 className="font-medium">Table {index + 1}</h4>
                          {perTableCsv && (
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() =>
                                downloadFileFromURL(perTableCsv, `${activeFile.name}_table_${index}.csv`)
                              }
                            >
                              <Download className="w-4 h-4 mr-2" />
                              CSV
                            </Button>
                          )}
                        </div>
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead className="bg-gray-100">
                              <tr>
                                {headers.map((header, i) => (
                                  <th
                                    key={i}
                                    className="px-4 py-2 text-left font-medium text-gray-700 border-b"
                                  >
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {rows.map((row, i) => (
                                <tr key={i} className="hover:bg-gray-50">
                                  {row.map((cell, j) => (
                                    <td key={j} className="px-4 py-2 text-sm border-b">
                                      {cell}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <Card className="p-3">
                    <div className="text-sm">No tables detected.</div>
                  </Card>
                )}
              </TabsContent>

              {/* IMAGES TAB */}
              <TabsContent value="images" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">Original Document</h4>
                    <div className="border rounded-lg p-4 bg-gray-50">
                      {results.original_image ? (
                        <img
                          src={`${API_BASE}${results.original_image}`}
                          alt="Uploaded document"
                          className="w-full h-48 object-contain rounded"
                        />
                      ) : (
                        <div className="text-sm text-gray-500">No preview available</div>
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Detected Tables</h4>
                    <div className="grid grid-cols-1 gap-4">
                      {results.tables?.length ? (
                        results.tables.map((t: any) => (
                          <div key={t.index} className="border rounded-lg p-4 bg-gray-50">
                            <img
                              src={`${API_BASE}${t.image}`}
                              alt={`table-${t.index}`}
                              className="w-full h-48 object-contain rounded"
                            />
                          </div>
                        ))
                      ) : results.table_crop_image ? (
                        <div className="border rounded-lg p-4 bg-gray-50">
                          <img
                            src={`${API_BASE}${results.table_crop_image}`}
                            alt="Cropped table"
                            className="w-full h-48 object-contain rounded"
                          />
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500">No table images</div>
                      )}
                    </div>
                  </div>
                </div>
              </TabsContent>

              {/* METADATA TAB */}
              <TabsContent value="metadata" className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm font-medium">Header JSON</div>
                    {results.header_json && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          downloadFileFromURL(results.header_json, `${activeFile.name}_header.json`)
                        }
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    )}
                  </div>
                  <pre className="text-sm overflow-x-auto">
                    {headerJson ? JSON.stringify(headerJson, null, 2) : '—'}
                  </pre>
                </div>

                {results.full_text_json && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-medium">Full OCR JSON</div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          downloadFileFromURL(results.full_text_json, `${activeFile.name}_full.json`)
                        }
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                    </div>
                    <div className="text-xs text-gray-500">
                      (Large – preview omitted here)
                    </div>
                  </div>
                )}
              </TabsContent>

              {/* WARNINGS TAB */}
              <TabsContent value="warnings" className="space-y-4">
                {results.warnings?.length > 0 ? (
                  <div className="space-y-2">
                    {results.warnings.map((warning: any, index: number) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                      >
                        <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                        <span className="text-sm text-yellow-800">
                          {warning?.header_warning
                            ? warning.header_warning
                            : `Table ${warning.table}, row ${warning.row ?? '—'}${
                                warning.field ? `, ${warning.field}` : ''
                              }: ${warning.message}`}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
                    <p className="text-gray-600">No warnings for this file</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </Card>
        );
      })()}
    </div>
  );
}
