import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { ToastProvider } from './components/ui/Toast';
import Home from './pages/Home';
import FileManager from './components/FileManager';
import './styles/globals.css';

// Theme Provider for dark mode
const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    
    if (newTheme) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  return (
    <div className={isDark ? 'dark' : ''}>
      {React.cloneElement(children, { isDark, toggleTheme })}
    </div>
  );
};

// Global Error Boundary
const GlobalErrorFallback = ({ error, resetErrorBoundary }) => (
  <div className="min-h-screen flex items-center justify-center bg-background p-4">
    <div className="max-w-md w-full text-center space-y-6">
      <div className="mx-auto w-20 h-20 bg-error-100 rounded-full flex items-center justify-center">
        <svg className="w-10 h-10 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-error-900">Application Error</h1>
        <p className="text-error-700">
          Something went wrong. Please try refreshing the page.
        </p>
        <details className="text-left mt-4">
          <summary className="cursor-pointer text-sm font-medium text-error-800 hover:text-error-900">
            Error Details
          </summary>
          <pre className="mt-2 p-3 bg-error-50 border border-error-200 rounded text-xs text-error-800 overflow-auto">
            {error.message}
          </pre>
        </details>
      </div>
      
      <div className="space-y-2">
        <button
          onClick={resetErrorBoundary}
          className="w-full px-4 py-2 bg-error-600 text-white rounded-md hover:bg-error-700 transition-colors"
        >
          Try Again
        </button>
        <button
          onClick={() => window.location.reload()}
          className="w-full px-4 py-2 border border-error-300 text-error-700 rounded-md hover:bg-error-50 transition-colors"
        >
          Refresh Page
        </button>
      </div>
    </div>
  </div>
);

// Main App Component
function App() {
  return (
    <ErrorBoundary
      FallbackComponent={GlobalErrorFallback}
      onError={(error, errorInfo) => {
        // Log error to monitoring service
        console.error('Global error caught:', error, errorInfo);
      }}
    >
      <ThemeProvider>
        <ToastProvider>
          <Router>
            <div className="App">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/home" element={<Home />} />
                <Route path="/file-manager" element={<FileManager />} />
                {/* Add more routes as needed */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </Router>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

// 404 Not Found Component
const NotFound = () => (
  <div className="min-h-screen flex items-center justify-center bg-background p-4">
    <div className="max-w-md w-full text-center space-y-6">
      <div className="mx-auto w-20 h-20 bg-muted rounded-full flex items-center justify-center">
        <svg className="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 20.4a7.962 7.962 0 01-5-1.691m0 0V9a3 3 0 015.196-2.121A3.001 3.001 0 0117 9v9.169l-3-2.647z" />
        </svg>
      </div>
      
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-foreground">404</h1>
        <h2 className="text-xl font-semibold text-foreground">Page Not Found</h2>
        <p className="text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
      </div>
      
      <div className="space-y-2">
        <a
          href="/"
          className="inline-block w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Go Home
        </a>
        <button
          onClick={() => window.history.back()}
          className="w-full px-4 py-2 border border-input text-foreground rounded-md hover:bg-accent transition-colors"
        >
          Go Back
        </button>
      </div>
    </div>
  </div>
);

export default App; 