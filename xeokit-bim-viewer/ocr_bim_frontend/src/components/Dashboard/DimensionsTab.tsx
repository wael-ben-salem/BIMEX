import React, { useState } from 'react';
import { Search, Ruler, Eye } from 'lucide-react';
import { ExtractedText } from '../../types';
import { useApp } from '../../context/AppContext';

interface DimensionsTabProps {
  data: ExtractedText[];
}

export function DimensionsTab({ data }: DimensionsTabProps) {
  const { state } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'confidence' | 'value'>('confidence');

  const parseDimension = (text: string) => {
    // Extract numeric value from dimension text like "24' - 6"" or "18' - 0""
    const match = text.match(/(\d+)'\s*-?\s*(\d+)"?/);
    if (match) {
      const feet = parseInt(match[1]);
      const inches = parseInt(match[2]);
      return feet * 12 + inches; // Convert to total inches
    }
    return 0;
  };

  const filteredData = data
    .filter(item => item.text.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      switch (sortBy) {
        case 'confidence':
          return b.confidence - a.confidence;
        case 'value':
          return parseDimension(b.text) - parseDimension(a.text);
        default:
          return 0;
      }
    });

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search dimensions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 border rounded-lg ${
              state.theme === 'dark'
                ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
                : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
            }`}
          />
        </div>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className={`px-3 py-2 border rounded-lg ${
            state.theme === 'dark'
              ? 'bg-gray-700 border-gray-600 text-white'
              : 'bg-white border-gray-300 text-gray-900'
          }`}
        >
          <option value="confidence">Sort by Confidence</option>
          <option value="value">Sort by Value</option>
        </select>
      </div>

      {/* Results Count */}
      <div className={`text-sm ${
        state.theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
      }`}>
        Showing {filteredData.length} dimensions
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredData.map((item) => (
          <div
            key={item.id}
            className={`p-4 rounded-lg border transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                : 'bg-white border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Ruler className="h-4 w-4 text-blue-500" />
                <span className={`font-medium ${
                  state.theme === 'dark' ? 'text-white' : 'text-gray-900'
                }`}>
                  {item.text}
                </span>
              </div>
              <button className={`p-1 rounded transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'hover:bg-gray-600 text-gray-400'
                  : 'hover:bg-gray-200 text-gray-500'
              }`}>
                <Eye className="h-3 w-3" />
              </button>
            </div>

            <div className="space-y-2">
              {/* Confidence */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Confidence:
                </span>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getConfidenceColor(item.confidence)}`}>
                    {Math.round(item.confidence )}%
                  </span>
                  <div className={`w-12 h-2 rounded-full ${
                    state.theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                  }`}>
                    <div
                      className={`h-2 rounded-full ${
                        item.confidence >=90 ? 'bg-green-500' :
                        item.confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${item.confidence }%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Converted Value */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Total Inches:
                </span>
                <span className={`text-sm font-medium ${
                  state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  {parseDimension(item.text)}"
                </span>
              </div>

              {/* Coordinates */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Position:
                </span>
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  ({item.x}, {item.y})
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredData.length === 0 && (
        <div className="text-center py-8">
          <p className={`text-sm ${
            state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
          }`}>
            No dimensions found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
}