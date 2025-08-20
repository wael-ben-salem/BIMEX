import React, { useState } from 'react';
import { Cuboid as Cube, Eye, EyeOff, Download, RotateCcw, Move } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export function BIMPreview() {
  const { state } = useApp();
  const [visibleLayers, setVisibleLayers] = useState(['structural', 'architectural']);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [rotation, setRotation] = useState({ x: 0, y: 0, z: 0 });

  const currentFile = state.currentFile || state.uploadedFiles[0];
  const analysisResult = currentFile ? state.analysisResults[currentFile.id] : null;

  const layers = [
    { id: 'structural', label: 'Structural', color: 'text-green-500', count: 12 },
    { id: 'architectural', label: 'Architectural', color: 'text-blue-500', count: 8 },
    { id: 'mep', label: 'MEP Systems', color: 'text-red-500', count: 15 },
    { id: 'civil', label: 'Civil', color: 'text-yellow-500', count: 6 },
  ];

  const toggleLayer = (layerId: string) => {
    setVisibleLayers(prev =>
      prev.includes(layerId)
        ? prev.filter(id => id !== layerId)
        : [...prev, layerId]
    );
  };

  const handleExport = (format: 'ifc' | 'dwg' | 'rvt') => {
    console.log(`Exporting to ${format.toUpperCase()}`);
    // Simulate export functionality
  };

  const resetView = () => {
    setRotation({ x: 0, y: 0, z: 0 });
    setSelectedElement(null);
  };

  if (!analysisResult) {
    return (
      <div className={`${
        state.theme === 'dark' ? 'bg-gray-800' : 'bg-white'
      } rounded-lg shadow-lg p-8 transition-colors duration-200`}>
        <div className="text-center">
          <Cube className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h3 className={`text-lg font-medium mb-2 ${
            state.theme === 'dark' ? 'text-white' : 'text-gray-900'
          }`}>
            3D BIM Preview
          </h3>
          <p className={`text-sm ${
            state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
          }`}>
            Process a blueprint to see the 3D model preview
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${
      state.theme === 'dark' ? 'bg-gray-800' : 'bg-white'
    } rounded-lg shadow-lg overflow-hidden transition-colors duration-200`}>
      {/* Header */}
      <div className={`px-6 py-4 border-b ${
        state.theme === 'dark' ? 'border-gray-700' : 'border-gray-200'
      }`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`text-lg font-medium ${
              state.theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              3D BIM Preview
            </h3>
            <p className={`text-sm ${
              state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            }`}>
              Generated from {currentFile?.name}
            </p>
          </div>

          {/* Export Controls */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleExport('ifc')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              <Download className="h-4 w-4" />
              <span>IFC</span>
            </button>
            <button
              onClick={() => handleExport('dwg')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              <Download className="h-4 w-4" />
              <span>DWG</span>
            </button>
            <button
              onClick={() => handleExport('rvt')}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              <Download className="h-4 w-4" />
              <span>Revit</span>
            </button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Layer Controls Sidebar */}
        <div className={`w-64 p-4 border-r ${
          state.theme === 'dark' ? 'border-gray-700 bg-gray-750' : 'border-gray-200 bg-gray-50'
        }`}>
          <h4 className={`text-sm font-medium mb-3 ${
            state.theme === 'dark' ? 'text-white' : 'text-gray-900'
          }`}>
            Layer Controls
          </h4>
          
          <div className="space-y-2">
            {layers.map((layer) => (
              <div
                key={layer.id}
                className={`flex items-center justify-between p-2 rounded-lg transition-colors duration-200 ${
                  visibleLayers.includes(layer.id)
                    ? state.theme === 'dark' ? 'bg-gray-700' : 'bg-white'
                    : state.theme === 'dark' ? 'bg-gray-800' : 'bg-gray-100'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleLayer(layer.id)}
                    className={`p-1 rounded ${layer.color}`}
                  >
                    {visibleLayers.includes(layer.id) ? (
                      <Eye className="h-4 w-4" />
                    ) : (
                      <EyeOff className="h-4 w-4" />
                    )}
                  </button>
                  <span className={`text-sm ${
                    state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    {layer.label}
                  </span>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  state.theme === 'dark' ? 'bg-gray-600 text-gray-300' : 'bg-gray-200 text-gray-600'
                }`}>
                  {layer.count}
                </span>
              </div>
            ))}
          </div>

          {/* View Controls */}
          <div className="mt-6">
            <h5 className={`text-sm font-medium mb-3 ${
              state.theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              View Controls
            </h5>
            <div className="space-y-2">
              <button
                onClick={resetView}
                className={`flex items-center space-x-2 w-full px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                  state.theme === 'dark'
                    ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    : 'bg-white hover:bg-gray-100 text-gray-700'
                }`}
              >
                <RotateCcw className="h-4 w-4" />
                <span>Reset View</span>
              </button>
              <button className={`flex items-center space-x-2 w-full px-3 py-2 rounded-lg text-sm transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  : 'bg-white hover:bg-gray-100 text-gray-700'
              }`}>
                <Move className="h-4 w-4" />
                <span>Pan Mode</span>
              </button>
            </div>
          </div>
        </div>

        {/* 3D Viewport */}
        <div className="flex-1">
          <div className={`relative h-96 ${
            state.theme === 'dark' ? 'bg-gray-900' : 'bg-gray-100'
          }`}>
            {/* Simulated 3D View */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="relative mb-4">
                  <Cube className={`h-32 w-32 mx-auto ${
                    state.theme === 'dark' ? 'text-gray-600' : 'text-gray-400'
                  }`} style={{
                    transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) rotateZ(${rotation.z}deg)`,
                    transition: 'transform 0.3s ease'
                  }} />
                  
                  {/* Simulated Elements */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="grid grid-cols-3 gap-1">
                      {visibleLayers.includes('structural') && (
                        <>
                          <div className="w-2 h-8 bg-green-500 opacity-60"></div>
                          <div className="w-2 h-8 bg-green-500 opacity-60"></div>
                          <div className="w-2 h-8 bg-green-500 opacity-60"></div>
                        </>
                      )}
                      {visibleLayers.includes('architectural') && (
                        <>
                          <div className="w-8 h-2 bg-blue-500 opacity-60"></div>
                          <div className="w-8 h-2 bg-blue-500 opacity-60"></div>
                          <div className="w-8 h-2 bg-blue-500 opacity-60"></div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  3D Model Preview
                </div>
                <div className={`text-xs mt-1 ${
                  state.theme === 'dark' ? 'text-gray-500' : 'text-gray-400'
                }`}>
                  Click and drag to rotate • Scroll to zoom
                </div>
              </div>
            </div>

            {/* Element Info Panel */}
            {selectedElement && (
              <div className={`absolute top-4 right-4 p-4 rounded-lg shadow-lg ${
                state.theme === 'dark' ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
              }`}>
                <h5 className={`font-medium mb-2 ${
                  state.theme === 'dark' ? 'text-white' : 'text-gray-900'
                }`}>
                  Element Properties
                </h5>
                <div className="space-y-1 text-sm">
                  <div className={state.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>
                    Type: Steel Beam
                  </div>
                  <div className={state.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>
                    Size: W14x30
                  </div>
                  <div className={state.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}>
                    Length: 24'-0"
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Status Bar */}
          <div className={`px-4 py-2 border-t text-xs ${
            state.theme === 'dark'
              ? 'border-gray-700 text-gray-400 bg-gray-750'
              : 'border-gray-200 text-gray-500 bg-gray-50'
          }`}>
            <div className="flex items-center justify-between">
              <div>
                Elements: {analysisResult.structuralElements.length} • 
                Symbols: {analysisResult.detectedSymbols.length} • 
                Areas: {analysisResult.areaCalculations.length}
              </div>
              <div>
                Rendering Mode: WebGL • FPS: 60
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}