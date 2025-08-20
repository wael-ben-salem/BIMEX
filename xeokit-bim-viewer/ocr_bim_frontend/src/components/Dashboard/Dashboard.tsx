import React, { useState } from 'react';
import { FileText, Target, Layers, Calculator, CheckCircle, Download, Clock } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { TextExtractionTab } from './TextExtractionTab';
import { DimensionsTab } from './DimensionsTab';
import { SymbolsTab } from './SymbolsTab';
import { ElementsTab } from './ElementsTab';
import { AreasTab } from './AreasTab';
import { startProcessing, getProcessingStatus, getAllResults, exportCSV, exportJSON } from '../../utils/api';
import { OCRAnalysisResult } from '../../types';

type TabType = 'text' | 'dimensions' | 'symbols' | 'elements' | 'areas';

const TABS = [
  { id: 'text' as TabType, label: 'Text Extraction', icon: FileText },
  { id: 'dimensions' as TabType, label: 'Dimensions', icon: Target },
  { id: 'symbols' as TabType, label: 'Symbols', icon: Layers },
  { id: 'elements' as TabType, label: 'Elements', icon: Calculator },
  { id: 'areas' as TabType, label: 'Areas/Zones', icon: CheckCircle },
];

export function Dashboard() {
  const { state, dispatch } = useApp();
  const [activeTab, setActiveTab] = useState<TabType>('text');
  const [loading, setLoading] = useState(false);

  const currentFile = state.currentFile;
  const analysisResult: OCRAnalysisResult | null = currentFile
    ? state.analysisResults[currentFile.id]
    : null;

  const pollProcessingStatus = async (backendId: string, fileId: string) => {
    try {
      const interval = setInterval(async () => {
        const statusRes = await getProcessingStatus(backendId);
        const status = statusRes.status; // 'pending' | 'processing' | 'completed' | 'failed'

        dispatch({
          type: 'UPDATE_FILE',
          payload: {
            id: fileId,
            updates: {
              status:
                status === 'processing'
                  ? 'processing'
                  : status === 'completed'
                  ? 'completed'
                  : 'error',
            },
          },
        });

        if (status === 'completed') {
          clearInterval(interval);
          const apiResult = await getAllResults(backendId);

          // Calculate OCR confidence
          const ocrResults = apiResult.ocr?.results || [];
          const ocrConfidence =
            ocrResults.reduce((sum: number, r: any) => sum + (r.confidence || 0), 0) /
            (ocrResults.length || 1);

          // Calculate symbols confidence
          const symbolResults = apiResult.vision?.symbols || [];
          const symbolsConfidence =
            symbolResults.reduce((sum: number, s: any) => sum + (s.confidence || 0), 0) /
            (symbolResults.length || 1);

          // Calculate elements confidence
          const elementResults = apiResult.vision?.elements || [];
          const elementsConfidence =
            elementResults.reduce((sum: number, e: any) => sum + (e.confidence || 0), 0) /
            (elementResults.length || 1);

          // Overall confidence
          const confidenceValues = [ocrConfidence, symbolsConfidence, elementsConfidence].filter(v => !isNaN(v));
          const overallConfidence =
            confidenceValues.reduce((sum, v) => sum + v, 0) / (confidenceValues.length || 1);

          const totalProcessingTime =
            (apiResult.ocr?.processing_time || 0) + (apiResult.vision?.processing_time || 0);

          const mappedResult: OCRAnalysisResult = {
            extractedText: ocrResults,
            detectedSymbols: symbolResults,
            structuralElements: elementResults,
            areaCalculations: [],
            confidenceScores: {
              overall: overallConfidence,
              text: ocrConfidence,
              symbols: symbolsConfidence,
              elements: elementsConfidence,
            },
            processingTime: totalProcessingTime,
            projectId: '',
            drawingFile: '',
            drawingType: 'architectural',
            processingStatus: 'pending'
          };

          dispatch({ type: 'SET_ANALYSIS_RESULT', payload: { fileId, result: mappedResult } });
        } else if (status === 'failed') {
          clearInterval(interval);
          alert(`Processing failed for file ${currentFile?.name}`);
        }
      }, 2000);
    } catch (err: any) {
      console.error('Polling failed:', err);
    }
  };

  const handleStartProcessing = async () => {
    if (!currentFile?.backendId) {
      alert('File not yet uploaded to backend. Please wait.');
      return;
    }

    try {
      setLoading(true);
      await startProcessing(currentFile.backendId, {
        enable_ocr: true,
        enable_vision: true,
        languages: ['eng'],
        use_llm: true,
      });

      dispatch({
        type: 'UPDATE_FILE',
        payload: { id: currentFile.id, updates: { status: 'processing' } },
      });

      pollProcessingStatus(currentFile.backendId, currentFile.id);
    } catch (err: any) {
      console.error(err);
      alert(`Failed to start processing: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderTabContent = () => {
    if (!analysisResult) {
      return (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <FileText className="h-16 w-16 mx-auto mb-4" />
            <p className="text-lg">No analysis results available</p>
            <p className="text-sm">Upload and process a blueprint to see results</p>
          </div>
        </div>
      );
    }

    switch (activeTab) {
      case 'text':
        return <TextExtractionTab data={analysisResult.extractedText} />;
      case 'dimensions':
        return <DimensionsTab data={analysisResult.extractedText?.filter(t => t.type === 'dimension')} />;
      case 'symbols':
        return <SymbolsTab data={analysisResult.detectedSymbols} />;
      case 'elements':
        return <ElementsTab data={analysisResult.structuralElements} />;
      case 'areas':
        return <AreasTab data={analysisResult.areaCalculations} />;
      default:
        return null;
    }
  };

  return (
    <div className={`${state.theme === 'dark' ? 'bg-gray-800' : 'bg-white'} rounded-lg shadow-lg overflow-hidden transition-colors duration-200`}>
      {/* Header */}
      <div className={`px-6 py-4 border-b ${state.theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`text-lg font-medium ${state.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>OCR Analysis Results</h3>
            {analysisResult && (
              <div className="flex items-center space-x-4 mt-2">
                <div className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  Overall Confidence: {Math.round(analysisResult.confidenceScores?.overall || 0)}%
                </div>
                <div className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  Processing Time: {analysisResult.processingTime?.toFixed(2) || 0}s
                </div>
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handleStartProcessing}
              disabled={!currentFile || loading || currentFile.status === 'processing'}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                currentFile && currentFile.backendId
                  ? state.theme === 'dark'
                    ? 'bg-blue-700 hover:bg-blue-600 text-white'
                    : 'bg-blue-100 hover:bg-blue-200 text-blue-800'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              <Clock className="h-4 w-4" />
              <span>{currentFile?.status === 'processing' ? 'Processing...' : 'Start Processing'}</span>
            </button>

            {/* Export buttons safely handle undefined backendId */}
            <button
              onClick={() => currentFile?.backendId && exportJSON(currentFile.backendId)}
              disabled={!currentFile?.backendId}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              <Download className="h-4 w-4" />
              <span>Export JSON</span>
            </button>

            <button
              onClick={() => currentFile?.backendId && exportCSV(currentFile.backendId)}
              disabled={!currentFile?.backendId}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              <Download className="h-4 w-4" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className={`border-b ${state.theme === 'dark' ? 'border-gray-700' : 'border-gray-200'}`}>
        <nav className="flex space-x-8 px-6">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  isActive
                    ? 'border-blue-500 text-blue-600'
                    : state.theme === 'dark'
                    ? 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {analysisResult && (
                  <span
                    className={`ml-2 px-2 py-1 rounded-full text-xs ${
                      isActive
                        ? 'bg-blue-100 text-blue-800'
                        : state.theme === 'dark'
                        ? 'bg-gray-700 text-gray-300'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {tab.id === 'text' && analysisResult.extractedText?.length}
                    {tab.id === 'dimensions' && analysisResult.extractedText?.filter(t => t.type === 'dimension').length}
                    {tab.id === 'symbols' && analysisResult.detectedSymbols?.length}
                    {tab.id === 'elements' && analysisResult.structuralElements?.length}
                    {tab.id === 'areas' && analysisResult.areaCalculations?.length}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="p-6">{renderTabContent()}</div>
    </div>
  );
}
