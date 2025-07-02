import React, { useState, useCallback, useEffect, useMemo } from "react";
import { ErrorBoundary } from "react-error-boundary";
import Cards from "../components/Cards";
import TemplateForm from "../components/TemplateForm";
import TestCaseForm from "../components/TestCaseForm";

// Error fallback component
const ErrorFallback = ({ error, resetErrorBoundary, componentName }) => (
  <div className="error-container" role="alert" aria-live="assertive">
    <h2>Something went wrong</h2>
    <details>
      <summary>Error Details</summary>
      <pre>{error.message}</pre>
      {componentName && <p>Component: {componentName}</p>}
    </details>
    <button onClick={resetErrorBoundary}>Try Again</button>
  </div>
);

// Loading component
const LoadingSpinner = ({ message = "Loading..." }) => (
  <div className="loading-container" role="status" aria-live="polite">
    <div className="spinner" />
    <p>{message}</p>
  </div>
);

// Navigation breadcrumb
const Breadcrumb = ({ selectedCard, onNavigate }) => {
  const breadcrumbItems = useMemo(() => {
    const items = [{ label: 'Home', value: null }];
    if (selectedCard === 'template') {
      items.push({ label: 'Template Form', value: 'template' });
    } else if (selectedCard === 'testCases') {
      items.push({ label: 'Test Cases', value: 'testCases' });
    }
    return items;
  }, [selectedCard]);

  return (
    <nav aria-label="Breadcrumb" className="breadcrumb-nav">
      <ol>
        {breadcrumbItems.map((item, index) => (
          <li key={item.value || 'home'}>
            {index > 0 && <span>/</span>}
            {index === breadcrumbItems.length - 1 ? (
              <span aria-current="page">{item.label}</span>
            ) : (
              <button onClick={() => onNavigate(item.value)}>
                {item.label}
              </button>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
};

const Home = () => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [componentHistory, setComponentHistory] = useState(['home']);

  // Handle card selection with loading state
  const handleCardSelect = useCallback(async (cardType) => {
    try {
      setError(null);
      setIsLoading(true);
      
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setSelectedCard(cardType);
      setComponentHistory(prev => [...prev, cardType]);
    } catch (err) {
      setError(`Failed to load ${cardType} component: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Handle navigation back
  const handleBack = useCallback(() => {
    try {
      setError(null);
      setSelectedCard(null);
      setComponentHistory(prev => prev.slice(0, -1));
    } catch (err) {
      setError(`Navigation error: ${err.message}`);
    }
  }, []);

  // Handle breadcrumb navigation
  const handleBreadcrumbNavigate = useCallback((value) => {
    try {
      setError(null);
      setSelectedCard(value);
      
      if (value === null) {
        setComponentHistory(['home']);
      } else {
        setComponentHistory(['home', value]);
      }
    } catch (err) {
      setError(`Navigation error: ${err.message}`);
    }
  }, []);

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && selectedCard) {
        event.preventDefault();
        handleBack();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedCard, handleBack]);

  // Error recovery
  const handleErrorRecovery = useCallback(() => {
    setError(null);
    setSelectedCard(null);
    setIsLoading(false);
    setComponentHistory(['home']);
  }, []);

  // Render current component
  const renderCurrentComponent = useMemo(() => {
    if (isLoading) {
      return <LoadingSpinner message="Loading component..." />;
    }

    if (error) {
      return (
        <div className="error-container" role="alert">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={handleErrorRecovery}>Return to Home</button>
        </div>
      );
    }

    switch (selectedCard) {
      case 'template':
        return (
          <ErrorBoundary
            FallbackComponent={(props) => 
              <ErrorFallback {...props} componentName="TemplateForm" />
            }
            onReset={handleErrorRecovery}
          >
            <TemplateForm onBack={handleBack} />
          </ErrorBoundary>
        );
      
      case 'testCases':
        return (
          <ErrorBoundary
            FallbackComponent={(props) => 
              <ErrorFallback {...props} componentName="TestCaseForm" />
            }
            onReset={handleErrorRecovery}
          >
            <TestCaseForm onBack={handleBack} />
          </ErrorBoundary>
        );
      
      default:
        return (
          <ErrorBoundary
            FallbackComponent={(props) => 
              <ErrorFallback {...props} componentName="Cards" />
            }
            onReset={handleErrorRecovery}
          >
            <Cards onSelect={handleCardSelect} />
          </ErrorBoundary>
        );
    }
  }, [selectedCard, isLoading, error, handleCardSelect, handleBack, handleErrorRecovery]);

  return (
    <ErrorBoundary
      FallbackComponent={(props) => 
        <ErrorFallback {...props} componentName="Home" />
      }
      onReset={handleErrorRecovery}
    >
      <div className="home-container" role="main" aria-label="Main application content">
        {/* Skip to content link for accessibility */}
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>

        {/* Header with title and navigation */}
        <header className="home-header">
          <h1>Test Case Generator</h1>
          <Breadcrumb 
            selectedCard={selectedCard} 
            onNavigate={handleBreadcrumbNavigate} 
          />
        </header>

        {/* Main content area */}
        <main id="main-content" className="home-main" tabIndex="-1">
          {renderCurrentComponent}
        </main>

        {/* Footer with help text */}
        <footer className="home-footer">
          <p>
            Use the cards above to navigate between different sections. 
            Press <kbd>ESC</kbd> to go back.
          </p>
        </footer>
      </div>
    </ErrorBoundary>
  );
};

export default Home; 