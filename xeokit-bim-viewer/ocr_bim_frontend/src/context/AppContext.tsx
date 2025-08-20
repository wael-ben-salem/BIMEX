import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { DrawingFile, OCRAnalysisResult } from '../types';

interface AppState {
  theme: 'light' | 'dark';
  uploadedFiles: DrawingFile[];
  currentFile: DrawingFile | null;
  analysisResults: Record<string, OCRAnalysisResult>;
  selectedLayer: string[];
  viewMode: 'original' | 'processed' | 'comparison';
  isProcessing: boolean;
}

type AppAction =
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'ADD_FILE'; payload: DrawingFile }
  | { type: 'UPDATE_FILE'; payload: { id: string; updates: Partial<DrawingFile> } }
  | { type: 'REMOVE_FILE'; payload: string }
  | { type: 'SET_CURRENT_FILE'; payload: string | null } // uses local id
  | { type: 'SET_ANALYSIS_RESULT'; payload: { fileId: string; result: OCRAnalysisResult } }
  | { type: 'TOGGLE_LAYER'; payload: string }
  | { type: 'SET_VIEW_MODE'; payload: 'original' | 'processed' | 'comparison' }
  | { type: 'SET_PROCESSING'; payload: boolean };

const initialState: AppState = {
  theme: 'light',
  uploadedFiles: [],
  currentFile: null,
  analysisResults: {},
  selectedLayer: ['text', 'symbols', 'elements'],
  viewMode: 'processed',
  isProcessing: false,
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'ADD_FILE':
      return { ...state, uploadedFiles: [...state.uploadedFiles, action.payload] };
    case 'UPDATE_FILE':
      return {
        ...state,
        uploadedFiles: state.uploadedFiles.map(file =>
          file.id === action.payload.id ? { ...file, ...action.payload.updates } : file
        ),
        currentFile:
          state.currentFile?.id === action.payload.id
            ? { ...state.currentFile, ...action.payload.updates }
            : state.currentFile,
      };
    case 'REMOVE_FILE':
      return {
        ...state,
        uploadedFiles: state.uploadedFiles.filter(file => file.id !== action.payload),
        currentFile: state.currentFile?.id === action.payload ? null : state.currentFile,
      };
    case 'SET_CURRENT_FILE':
      const file = state.uploadedFiles.find(f => f.id === action.payload) || null;
      return { ...state, currentFile: file };
    case 'SET_ANALYSIS_RESULT':
      return {
        ...state,
        analysisResults: {
          ...state.analysisResults,
          [action.payload.fileId]: action.payload.result,
        },
      };
    case 'TOGGLE_LAYER':
      const layer = action.payload;
      const selectedLayer = state.selectedLayer.includes(layer)
        ? state.selectedLayer.filter(l => l !== layer)
        : [...state.selectedLayer, layer];
      return { ...state, selectedLayer };
    case 'SET_VIEW_MODE':
      return { ...state, viewMode: action.payload };
    case 'SET_PROCESSING':
      return { ...state, isProcessing: action.payload };
    default:
      return state;
  }
}

const AppContext = createContext<{
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
} | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within an AppProvider');
  return context;
}
