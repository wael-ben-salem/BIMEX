import React, { useCallback, useState } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { useApp } from '../../context/AppContext';
import { DrawingFile, DrawingType } from '../../types';
import { uploadFileToBackend } from '../../utils/api';

const DRAWING_TYPE_LABELS: Record<DrawingType, string> = {
  architectural: 'Architectural',
  structural: 'Structural',
  civil: 'Civil Engineering',
  infrastructure: 'Infrastructure',
  mep: 'MEP Systems',
  general: 'General'
};

const DRAWING_TYPE_COLORS: Record<DrawingType, string> = {
  architectural: 'bg-blue-100 text-blue-800',
  structural: 'bg-green-100 text-green-800',
  civil: 'bg-yellow-100 text-yellow-800',
  infrastructure: 'bg-purple-100 text-purple-800',
  mep: 'bg-red-100 text-red-800',
  general: 'bg-gray-100 text-gray-800'
};

export function FileUpload() {
  const { state, dispatch } = useApp();
  const [dragActive, setDragActive] = useState(false);

  const classifyDrawingType = (filename: string): DrawingType => {
    const name = filename.toLowerCase();
    if (name.includes('floor') || name.includes('elevation') || name.includes('architectural')) return 'architectural';
    if (name.includes('structural') || name.includes('beam') || name.includes('foundation')) return 'structural';
    if (name.includes('civil') || name.includes('site') || name.includes('utility')) return 'civil';
    if (name.includes('bridge') || name.includes('highway') || name.includes('tunnel')) return 'infrastructure';
    if (name.includes('electrical') || name.includes('plumbing') || name.includes('hvac') || name.includes('mep')) return 'mep';
    return 'general';
  };

  const handleFiles = useCallback((files: FileList) => {
    Array.from(files).forEach(async (file) => {
      const tempId = Math.random().toString(36).substr(2, 9);

      const drawingFile: DrawingFile = {
        id: tempId,
        backendId: undefined, // store backend ID after upload
        name: file.name,
        type: file.type,
        size: file.size,
        drawingType: classifyDrawingType(file.name),
        uploadProgress: 0,
        status: 'uploading',
        thumbnail: URL.createObjectURL(file),
      };

      dispatch({ type: 'ADD_FILE', payload: drawingFile });

      try {
        const res = await uploadFileToBackend(file);

        dispatch({
          type: 'UPDATE_FILE',
          payload: {
            id: tempId,
            updates: {
              backendId: res.data.id,
              uploadProgress: 100,
              status: 'completed',
              name: res.data.filename,
              size: res.data.size_kb ? res.data.size_kb * 1024 : file.size,
              thumbnail: `http://localhost:8001/ocr/files/${res.data.id}/thumbnail`,
            },
          },
        });
      } catch (error: any) {
        dispatch({ type: 'UPDATE_FILE', payload: { id: tempId, updates: { status: 'error' } } });
        console.error('Upload failed:', error.message);
      }
    });
  }, [dispatch]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) handleFiles(e.target.files);
  };

  const removeFile = (fileId: string) => {
    dispatch({ type: 'REMOVE_FILE', payload: fileId });
    if (state.currentFile?.id === fileId) dispatch({ type: 'SET_CURRENT_FILE', payload: null });
  };

  const setCurrentFile = (file: DrawingFile) => {
    dispatch({ type: 'SET_CURRENT_FILE', payload: file.id });
  };

  const getStatusIcon = (status: DrawingFile['status']) => {
    switch (status) {
      case 'uploading': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'processing': return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />;
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  return (
    <div className={`${state.theme === 'dark' ? 'bg-gray-800' : 'bg-white'} rounded-lg shadow-lg p-6 transition-colors duration-200`}>
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
          dragActive ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20' :
          state.theme === 'dark' ? 'border-gray-600 hover:border-gray-500' : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
      >
        <input
          type="file" multiple accept=".pdf,.jpg,.jpeg,.png,.tiff,.dwg,.dxf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <Upload className={`mx-auto h-12 w-12 mb-4 ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-400'}`} />
        <h3 className={`text-lg font-medium mb-2 ${state.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Upload Technical Drawings</h3>
        <p className={`text-sm mb-4 ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>Drag and drop files here, or click to browse</p>
        <p className={`text-xs ${state.theme === 'dark' ? 'text-gray-500' : 'text-gray-400'}`}>Supports: PDF, JPG, PNG, TIFF, DWG, DXF</p>
      </div>

      {state.uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className={`text-lg font-medium mb-4 ${state.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>Uploaded Files ({state.uploadedFiles.length})</h4>
          <div className="space-y-3">
            {state.uploadedFiles.map((file) => (
              <div
                key={file.id} onClick={() => setCurrentFile(file)}
                className={`flex items-center space-x-4 p-4 rounded-lg border transition-colors duration-200 cursor-pointer ${
                  state.theme === 'dark' ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
                } ${state.currentFile?.id === file.id ? 'ring-2 ring-blue-500' : ''}`}
              >
                <div className="flex-shrink-0">
                  {file.thumbnail ? <img src={file.thumbnail} alt={file.name} className="h-32 w-auto object-contain rounded" /> :
                    <div className={`h-32 w-32 rounded flex items-center justify-center ${state.theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'}`}>
                      <FileText className="h-12 w-12 text-gray-400" />
                    </div>}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <p className={`text-sm font-medium truncate ${state.theme === 'dark' ? 'text-white' : 'text-gray-900'}`}>{file.name}</p>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${DRAWING_TYPE_COLORS[file.drawingType]}`}>
                      {DRAWING_TYPE_LABELS[file.drawingType]}
                    </span>
                  </div>

                  <div className="flex items-center space-x-4">
                    <p className={`text-xs ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                    {file.dimensions && <p className={`text-xs ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}>{file.dimensions.width} × {file.dimensions.height}</p>}
                  </div>

                  {file.status === 'uploading' && (
                    <div className={`mt-2 w-full rounded-full h-2 ${state.theme === 'dark' ? 'bg-gray-600' : 'bg-gray-200'}`}>
                      <div className="bg-blue-600 h-2 rounded-full transition-all duration-300" style={{ width: `${file.uploadProgress}%` }}></div>
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-2">
                  {getStatusIcon(file.status)}
                  <button onClick={(e) => { e.stopPropagation(); removeFile(file.id); }}
                    className={`p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200 ${state.theme === 'dark' ? 'text-gray-400' : 'text-gray-500'}`}
                    aria-label="Remove file">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
