// src/App.tsx (AppContent without BIMPreview)
import React, { useEffect } from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Header } from './components/Layout/Header';
import { FileUpload } from './components/FileUpload/FileUpload';
import { BlueprintViewer } from './components/BlueprintViewer/BlueprintViewer';
import { Dashboard } from './components/Dashboard/Dashboard';

function AppContent() {
  const { state, dispatch } = useApp();

useEffect(() => {
  // When uploadedFiles change and no current file set, set the first file's ID as current
  if (!state.currentFile && state.uploadedFiles.length > 0) {
    dispatch({ type: 'SET_CURRENT_FILE', payload: state.uploadedFiles[0].id });
  }
}, [state.uploadedFiles, state.currentFile, dispatch]);


  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      state.theme === 'dark' 
        ? 'bg-gray-900' 
        : 'bg-gray-50'
    }`}>
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - File Upload */}
          <div className="lg:col-span-1">
            <FileUpload />
          </div>

          {/* Right Column - Blueprint Viewer */}
          <div className="lg:col-span-2">
            <BlueprintViewer />
          </div>
        </div>

        {/* Dashboard Section */}
        <div className="mt-8">
          <Dashboard />
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;
