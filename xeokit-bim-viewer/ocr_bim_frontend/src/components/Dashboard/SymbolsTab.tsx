import React, { useState } from 'react';
import { Search, Package, Eye } from 'lucide-react';
import { DetectedSymbol } from '../../types';
import { useApp } from '../../context/AppContext';

interface SymbolsTabProps {
  data: DetectedSymbol[];
}

export function SymbolsTab({ data }: SymbolsTabProps) {
  const { state } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Map bbox to x, y, width, height for easier display
  const mappedData = (data || []).map((symbol, index) => {
    const [x1, y1, x2, y2] = symbol.bbox;
    return {
      ...symbol,
      x: x1,
      y: y1,
      width: x2 - x1,
      height: y2 - y1,
      id: symbol.id ?? index,
    };
  });

  // Filter by name
  const filteredData = mappedData
    .filter(item => item.name && item.confidence !== undefined)
    .filter(item => item.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => b.confidence - a.confidence);

  const getCategoryColor = (name: string) => {
    switch (name.toLowerCase()) {
      case 'window_symbol':
        return 'bg-blue-100 text-blue-800';
      case 'door_symbol':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search symbols..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 border rounded-lg ${
              state.theme === 'dark'
                ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
            }`}
          />
        </div>
      </div>

      <div className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
        Showing {filteredData.length} of {data.length} symbols
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredData.map((symbol) => (
            <div
              key={symbol.id}
              className={`p-4 rounded-lg border transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                  : 'bg-white border-gray-200 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <Package className="h-8 w-8 text-blue-500" />
                <button
                  className={`p-1 rounded transition-colors duration-200 ${
                    state.theme === 'dark'
                      ? 'hover:bg-gray-600 text-gray-400'
                      : 'hover:bg-gray-200 text-gray-500'
                  }`}
                >
                  <Eye className="h-4 w-4" />
                </button>
              </div>

              <h4 className={`font-medium mb-2 capitalize ${state.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                {symbol.name.replace('_', ' ')}
              </h4>

              <div className="space-y-2 mb-3">
                <div className="flex items-center justify-between">
                  <span className={`text-xs ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Type:</span>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(symbol.name)}`}>
                    {symbol.name}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className={`text-xs ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Confidence:</span>
                  <span className={`text-xs font-medium ${getConfidenceColor(symbol.confidence)}`}>
                    {Math.round(symbol.confidence )}%
                  </span>
                </div>

                <div className={`flex items-center justify-between text-xs ${state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                  <span>Position / Size:</span>
                  <span>
                    (x: {symbol.x}, y: {symbol.y}, w: {symbol.width}, h: {symbol.height})
                  </span>
                </div>
              </div>

              <div className={`w-full h-2 rounded-full ${state.theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'}`}>
                <div
                  className={`h-2 rounded-full ${
                    symbol.confidence >= 90
                      ? 'bg-green-500'
                      : symbol.confidence >= 0.7
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${symbol.confidence }%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {filteredData.length === 0 && (
        <div className="text-center py-8">
          <Package className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            No symbols found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
}
