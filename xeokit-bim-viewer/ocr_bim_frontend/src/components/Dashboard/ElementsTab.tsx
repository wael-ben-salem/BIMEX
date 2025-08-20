import React, { useState } from 'react';
import { Search, Box, Eye } from 'lucide-react';
import { StructuralElement } from '../../types';
import { useApp } from '../../context/AppContext';

interface ElementsTabProps {
  data: StructuralElement[];
}

export function ElementsTab({ data }: ElementsTabProps) {
  const { state } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const filteredData = data
    .filter(item => {
      const elementType = item.element_type ?? ''; // use element_typee
      const matchesSearch = elementType.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === 'all' || elementType === typeFilter;
      return matchesSearch && matchesType;
    })
    .sort((a, b) => b.confidence - a.confidence);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'wall': return 'bg-blue-100 text-blue-800';
      case 'beam': return 'bg-green-100 text-green-800';
      case 'column': return 'bg-purple-100 text-purple-800';
      case 'slab': return 'bg-yellow-100 text-yellow-800';
      case 'foundation': return 'bg-gray-100 text-gray-800';
      case 'road': return 'bg-orange-100 text-orange-800';
      case 'pipe': return 'bg-red-100 text-red-800';
      case 'duct': return 'bg-indigo-100 text-indigo-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
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
            placeholder="Search elements..."
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
          <option value="wall">Walls</option>
          <option value="beam">Beams</option>
          <option value="column">Columns</option>
          <option value="slab">Slabs</option>
          <option value="foundation">Foundations</option>
          <option value="road">Roads</option>
          <option value="pipe">Pipes</option>
          <option value="duct">Ducts</option>
        </select>
      </div>

      {/* Results Count */}
      <div className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-600'}`}>
        Showing {filteredData.length} of {data.length} elements
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredData.map((element, index) => (
          <div
            key={element.id ?? index} // fallback to index if no id
            className={`p-6 rounded-lg border transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                : 'bg-white border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Box className="h-6 w-6 text-blue-500" />
                <h4 className={`text-lg font-medium capitalize ${state.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>
                  {element.element_type}
                </h4>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(element.element_type)}`}>
                  {element.element_type}
                </span>
              </div>
              <button className={`p-2 rounded transition-colors duration-200 ${
                state.theme === 'dark'
                  ? 'hover:bg-gray-600 text-gray-400'
                  : 'hover:bg-gray-200 text-gray-500'
              }`}>
                <Eye className="h-4 w-4" />
              </button>
            </div>

            {/* Confidence */}
            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between">
                <span className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  Confidence:
                </span>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getConfidenceColor(element.confidence)}`}>
                    {Math.round(element.confidence )}%
                  </span>
                  <div className={`w-16 h-2 rounded-full ${state.theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'}`}>
                    <div
                      className={`h-2 rounded-full ${
                        element.confidence >= 90? 'bg-green-500' :
                        element.confidence >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${element.confidence }%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Coordinates */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
                  Position / Size:
                </span>
                <span className={`text-sm ${state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'}`}>
                  (x: {element.x}, y: {element.y}, w: {element.width}, h: {element.height})
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredData.length === 0 && (
        <div className="text-center py-8">
          <Box className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className={`text-sm ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>
            No elements found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
}
