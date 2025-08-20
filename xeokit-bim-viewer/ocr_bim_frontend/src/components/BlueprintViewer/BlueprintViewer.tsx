import React, { useState, useRef } from 'react';
import { ZoomIn, ZoomOut, RotateCw, Eye, EyeOff, Layers } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { DetectedSymbol } from '../../types';

export function BlueprintViewer() {
  const { state, dispatch } = useApp();
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [rotation, setRotation] = useState(0);
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const currentFile = state.currentFile || state.uploadedFiles[0] || null;
  const analysisResult = currentFile ? state.analysisResults[currentFile.id] : null;

  const handleZoomIn = () => setZoom(prev => Math.min(prev * 1.2, 5));
  const handleZoomOut = () => setZoom(prev => Math.max(prev / 1.2, 0.1));
  const handleRotate = () => setRotation(prev => (prev + 90) % 360);
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setRotation(0);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsPanning(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => setIsPanning(false);

  const toggleLayer = (layer: string) => {
    dispatch({ type: 'TOGGLE_LAYER', payload: layer });
  };

  const renderAnnotations = () => {
    if (!analysisResult || !state.selectedLayer.length) return null;

    return (
      <div className="absolute inset-0 pointer-events-none">
        {/* Text Annotations */}
        {state.selectedLayer.includes('text') &&
          (analysisResult.extractedText || []).map((text) => (
            <div
              key={text.id}
              className="absolute border border-blue-400 bg-blue-400/20 rounded"
              style={{
                left: `${(text.x ?? 0) / 1200 * 100}%`,
                top: `${(text.y ?? 0) / 800 * 100}%`,
                width: `${(text.width ?? 0) / 1200 * 100}%`,
                height: `${(text.height ?? 0) / 800 * 100}%`,
              }}
            >
              <div className="absolute -top-6 left-0 bg-blue-600 text-white px-1 py-0.5 rounded text-xs whitespace-nowrap">
                {text.text} ({Math.round(text.confidence * 100)}%)
              </div>
            </div>
          ))}

{/* Symbol Annotations */}
{state.selectedLayer.includes('symbols') &&
  (analysisResult.detectedSymbols || []).map((symbol: DetectedSymbol, idx) => {
    const [x1, y1, x2, y2] = symbol.bbox;
    const x = x1;
    const y = y1;
    const width = x2 - x1;
    const height = y2 - y1;
    
    return (
      <div
        key={symbol.id ?? idx}
        className="absolute border border-green-400 bg-green-400/20 rounded"
        style={{
          left: `${x / 1200 * 100}%`,
          top: `${y / 800 * 100}%`,
          width: `${width / 1200 * 100}%`,
          height: `${height / 800 * 100}%`,
        }}
      >
        <div className="absolute -top-6 left-0 bg-green-600 text-white px-1 py-0.5 rounded text-xs whitespace-nowrap">
          {symbol.name} ({Math.round(symbol.confidence * 100)}%)
        </div>
      </div>
    );
  })}


        {/* Element Annotations */}
        {state.selectedLayer.includes('elements') &&
          (analysisResult.structuralElements || []).map((element) => (
            <div
              key={element.id}
              className="absolute border border-purple-400 bg-purple-400/20"
              style={{
                left: `${(element.x ?? 0) / 1200 * 100}%`,
                top: `${(element.y ?? 0) / 800 * 100}%`,
                width: `${(element.width ?? 0) / 1200 * 100}%`,
                height: `${(element.height ?? 0) / 800 * 100}%`,
              }}
            >
              <div className="absolute -top-6 left-0 bg-purple-600 text-white px-1 py-0.5 rounded text-xs whitespace-nowrap">
                {element.type} ({Math.round(element.confidence * 100)}%)
              </div>
            </div>
          ))}
      </div>
    );
  };

  if (!currentFile) {
    return (
      <div
        className={`${
          state.theme === 'dark' ? 'bg-gray-800' : 'bg-white'
        } rounded-lg shadow-lg p-8 text-center transition-colors duration-200`}
      >
        <div className="text-gray-400 mb-4">
          <Layers className="h-16 w-16 mx-auto mb-4" />
          <p className="text-lg">No blueprint selected</p>
          <p className="text-sm">Upload a file to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`${
        state.theme === 'dark' ? 'bg-gray-800' : 'bg-white'
      } rounded-lg shadow-lg overflow-hidden transition-colors duration-200`}
    >
      {/* Header */}
      <div
        className={`px-6 py-4 border-b ${
          state.theme === 'dark' ? 'border-gray-700' : 'border-gray-200'
        }`}
      >
        <div className="flex items-center justify-between">
          <div>
            <h3
              className={`text-lg font-medium ${
                state.theme === 'dark' ? 'text-white' : 'text-gray-900'
              }`}
            >
              {currentFile.name}
            </h3>
            <p
              className={`text-sm ${
                state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
              }`}
            >
              {currentFile.drawingType} •{' '}
              {(currentFile.size / 1024 / 1024).toFixed(1)} MB
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center space-x-2">
            <select
              value={state.viewMode}
              onChange={(e) =>
                dispatch({ type: 'SET_VIEW_MODE', payload: e.target.value as any })
              }
              className={`px-3 py-2 rounded-lg border text-sm ${
                state.theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-white'
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              <option value="original">Original</option>
              <option value="processed">Processed</option>
              <option value="comparison">Comparison</option>
            </select>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div
        className={`px-6 py-4 border-b flex items-center justify-between ${
          state.theme === 'dark' ? 'border-gray-700' : 'border-gray-200'
        }`}
      >
        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className={`p-2 rounded-lg transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            }`}
          >
            <ZoomOut className="h-4 w-4" />
          </button>
          <span
            className={`text-sm px-2 ${
              state.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
            }`}
          >
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className={`p-2 rounded-lg transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            }`}
          >
            <ZoomIn className="h-4 w-4" />
          </button>
          <button
            onClick={handleRotate}
            className={`p-2 rounded-lg transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            }`}
          >
            <RotateCw className="h-4 w-4" />
          </button>
          <button
            onClick={handleReset}
            className={`px-3 py-2 text-sm rounded-lg transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
            }`}
          >
            Reset
          </button>
        </div>

        {/* Layer Controls */}
        <div className="flex items-center space-x-2">
          <span
            className={`text-sm ${
              state.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
            }`}
          >
            Layers:
          </span>
          {['text', 'symbols', 'elements'].map((layer) => (
            <button
              key={layer}
              onClick={() => toggleLayer(layer)}
              className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.selectedLayer.includes(layer)
                  ? 'bg-blue-600 text-white'
                  : state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              {state.selectedLayer.includes(layer) ? (
                <Eye className="h-3 w-3" />
              ) : (
                <EyeOff className="h-3 w-3" />
              )}
              <span className="capitalize">{layer}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Viewer */}
      <div
        ref={containerRef}
        className="relative h-96 overflow-hidden cursor-move"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div
          className="absolute inset-0 flex items-center justify-center"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom}) rotate(${rotation}deg)`,
            transformOrigin: 'center center',
            transition: isPanning ? 'none' : 'transform 0.2s ease',
          }}
        >
          <img
            src={currentFile.url || currentFile.thumbnail}
            alt={currentFile.name}
            className="max-w-full max-h-full object-contain select-none"
            draggable={false}
          />
        </div>

        {/* Annotations Overlay */}
        {state.viewMode !== 'original' && analysisResult && renderAnnotations()}
      </div>

      {/* Coordinates Display */}
      <div
        className={`px-6 py-3 border-t text-xs ${
          state.theme === 'dark'
            ? 'border-gray-700 text-gray-400'
            : 'border-gray-200 text-gray-500'
        }`}
      >
        Pan: ({pan.x.toFixed(0)}, {pan.y.toFixed(0)}) • Zoom:{' '}
        {Math.round(zoom * 100)}% • Rotation: {rotation}°
      </div>
    </div>
  );
}
