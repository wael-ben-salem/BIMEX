import React, { useState } from 'react';
import { Search, Square, Eye, Calculator } from 'lucide-react';
import { AreaCalculation } from '../../types';
import { useApp } from '../../context/AppContext';

interface AreasTabProps {
  data: AreaCalculation[];
}

export function AreasTab({ data }: AreasTabProps) {
  const { state } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'area' | 'label'>('area');

  const filteredData = data
    .filter(item => {
      const matchesSearch = item.label.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === 'all' || item.type === typeFilter;
      return matchesSearch && matchesType;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'area':
          return b.area - a.area;
        case 'label':
          return a.label.localeCompare(b.label);
        default:
          return 0;
      }
    });

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'room':
        return 'bg-blue-100 text-blue-800';
      case 'zone':
        return 'bg-green-100 text-green-800';
      case 'section':
        return 'bg-purple-100 text-purple-800';
      case 'lot':
        return 'bg-yellow-100 text-yellow-800';
      case 'right-of-way':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const totalArea = filteredData.reduce((sum, area) => sum + area.area, 0);

  return (
    <div className="space-y-6">
      {/* Filters and Summary */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search areas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className={`pl-10 pr-4 py-2 border rounded-lg ${
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
            <option value="room">Rooms</option>
            <option value="zone">Zones</option>
            <option value="section">Sections</option>
            <option value="lot">Lots</option>
            <option value="right-of-way">Right-of-Way</option>
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
            <option value="area">Sort by Area</option>
            <option value="label">Sort by Name</option>
          </select>
        </div>

        {/* Summary Card */}
        <div className={`p-4 rounded-lg border ${
          state.theme === 'dark'
            ? 'bg-gray-700 border-gray-600'
            : 'bg-blue-50 border-blue-200'
        }`}>
          <div className="flex items-center space-x-2">
            <Calculator className="h-5 w-5 text-blue-500" />
            <div>
              <div className={`text-sm ${
                state.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
              }`}>
                Total Area
              </div>
              <div className={`text-lg font-bold ${
                state.theme === 'dark' ? 'text-white' : 'text-gray-900'
              }`}>
                {totalArea.toLocaleString()} sq ft
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className={`text-sm ${
        state.theme === 'dark' ? 'text-gray-400' : 'text-gray-600'
      }`}>
        Showing {filteredData.length} of {data.length} areas/zones
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredData.map((area) => (
          <div
            key={area.id}
            className={`p-6 rounded-lg border transition-colors duration-200 ${
              state.theme === 'dark'
                ? 'bg-gray-700 border-gray-600 hover:bg-gray-600'
                : 'bg-white border-gray-200 hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Square className="h-6 w-6 text-blue-500" />
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  getTypeColor(area.type)
                }`}>
                  {area.type}
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

            <h4 className={`text-lg font-medium mb-3 ${
              state.theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              {area.label}
            </h4>

            <div className="space-y-3">
              {/* Area */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Area:
                </span>
                <span className={`text-lg font-bold ${
                  state.theme === 'dark' ? 'text-white' : 'text-gray-900'
                }`}>
                  {area.area.toLocaleString()} {area.unit}
                </span>
              </div>

              {/* Perimeter */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Perimeter:
                </span>
                <span className={`text-sm font-medium ${
                  state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  {area.perimeter} ft
                </span>
              </div>

              {/* Coordinates Count */}
              <div className="flex items-center justify-between">
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                }`}>
                  Vertices:
                </span>
                <span className={`text-sm ${
                  state.theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                }`}>
                  {area.coordinates.length} points
                </span>
              </div>
            </div>

            {/* Area Visualization */}
            <div className={`mt-4 p-3 rounded border ${
              state.theme === 'dark' ? 'border-gray-600 bg-gray-800' : 'border-gray-200 bg-gray-50'
            }`}>
              <div className="text-xs text-center mb-2 text-gray-500">Area Preview</div>
              <svg
                viewBox="0 0 100 60"
                className="w-full h-12"
                style={{ maxHeight: '48px' }}
              >
                <polygon
                  points={area.coordinates.map(coord => 
                    `${(coord.x / Math.max(...area.coordinates.map(c => c.x))) * 90 + 5},${(coord.y / Math.max(...area.coordinates.map(c => c.y))) * 50 + 5}`
                  ).join(' ')}
                  fill="rgba(59, 130, 246, 0.3)"
                  stroke="rgb(59, 130, 246)"
                  strokeWidth="1"
                />
              </svg>
            </div>
          </div>
        ))}
      </div>

      {filteredData.length === 0 && (
        <div className="text-center py-8">
          <Square className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className={`text-sm ${
            state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
          }`}>
            No areas found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
}