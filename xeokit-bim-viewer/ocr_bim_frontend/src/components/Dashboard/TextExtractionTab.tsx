import React, { useState } from 'react';
import { Search, MapPin, Eye } from 'lucide-react';
import { ExtractedText } from '../../types';
import { useApp } from '../../context/AppContext';

interface TextExtractionTabProps {
  data?: ExtractedText[]; // make optional
}

export function TextExtractionTab({ data = [] }: TextExtractionTabProps) {
  const { state } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'confidence' | 'text' | 'type'>('confidence');

  const filteredData = data
    .filter(item => {
      const matchesSearch = item.text.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === 'all' || item.type === typeFilter;
      return matchesSearch && matchesType;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'confidence':
          return b.confidence - a.confidence;
        case 'text':
          return a.text.localeCompare(b.text);
        case 'type':
          return (a.type || '').localeCompare(b.type || '');
        default:
          return 0;
      }
    });

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTypeColor = (type?: string) => {
    switch (type) {
      case 'dimension':
        return 'bg-blue-100 text-blue-800';
      case 'label':
        return 'bg-green-100 text-green-800';
      case 'annotation':
        return 'bg-purple-100 text-purple-800';
      case 'title':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search extracted text..."
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
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className={`px-3 py-2 border rounded-lg ${
            state.theme === 'dark'
              ? 'bg-gray-700 border-gray-600 text-white'
              : 'bg-white border-gray-300 text-gray-900'
          }`}
        >
          <option value="all">All Types</option>
          <option value="dimension">Dimensions</option>
          <option value="label">Labels</option>
          <option value="annotation">Annotations</option>
          <option value="title">Titles</option>
        </select>

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
          <option value="text">Sort by Text</option>
          <option value="type">Sort by Type</option>
        </select>
      </div>

      {/* Results Count */}
      <div className={`text-sm ${
        state.theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
      }`}>
        Showing {filteredData.length} of {data.length} text elements
      </div>

      {/* Results Table */}
      <div className={`overflow-hidden rounded-lg border ${
        state.theme === 'dark' ? 'border-gray-700' : 'border-gray-200'
      }`}>
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className={state.theme === 'dark' ? 'bg-gray-700' : 'bg-gray-50'}>
            <tr>
              <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                state.theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
              }`}>Text</th>
              <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                state.theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
              }`}>Type</th>
              <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                state.theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
              }`}>Confidence</th>
              <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                state.theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
              }`}>Coordinates</th>
              <th className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider ${
                state.theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
              }`}>Actions</th>
            </tr>
          </thead>
          <tbody className={`divide-y ${
            state.theme === 'dark' 
              ? 'bg-gray-800 divide-gray-700' 
              : 'bg-white divide-gray-200'
          }`}>
            {filteredData.map((item, index) => (
              <tr key={index} className={state.theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}>
                <td className={`px-6 py-4 whitespace-nowrap ${
                  state.theme === 'dark' ? 'text-white' : 'text-gray-900'
                }`}>
                  <div className="font-medium">{item.text}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    getTypeColor(item.type)
                  }`}>
                    {item.type || 'unknown'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className={`text-sm font-medium ${getConfidenceColor(item.confidence)}`}>
                      {Math.round(item.confidence)}%
                    </div>
                    <div className={`ml-2 w-16 rounded-full h-2 ${
                      state.theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'
                    }`}>
                      <div
                        className={`h-2 rounded-full ${
                          item.confidence >= 90 ? 'bg-green-500' :
                          item.confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${item.confidence}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                  state.theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
                }`}>
                  <div className="flex items-center space-x-1">
                    <MapPin className="h-3 w-3" />
                    <span>
                      ({item.x ?? 0}, {item.y ?? 0})
                    </span>
                  </div>
                  <div className="text-xs mt-1">
                    {item.width ?? 0} × {item.height ?? 0}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <button className={`flex items-center space-x-1 px-2 py-1 rounded text-xs transition-colors duration-200 ${
                    state.theme === 'dark'
                      ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                  }`}>
                    <Eye className="h-3 w-3" />
                    <span>View</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredData.length === 0 && (
        <div className="text-center py-8">
          <p className={`text-sm ${
            state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
          }`}>
            No text elements found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
}
