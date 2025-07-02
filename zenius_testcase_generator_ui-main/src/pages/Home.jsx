import React, { useState, useCallback, useEffect, useMemo } from "react";
import { ErrorBoundary } from "react-error-boundary";
import { 
  DocumentTextIcon, 
  BeakerIcon, 
  CogIcon,
  HomeIcon,
  ChevronRightIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { FeatureCard } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { cn } from "../utils/cn";
import TemplateForm from "../components/TemplateForm";
import TestCaseForm from "../components/TestCaseForm";

// Error fallback component
const ErrorFallback = ({ error, resetErrorBoundary, componentName }) => (
  <div className="min-h-[400px] flex items-center justify-center p-8">
    <div className="max-w-md w-full text-center space-y-6">
      <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
        <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
      </div>
      
      <div className="space-y-2">
        <h3 className="text-xl font-semibold text-red-900">Something went wrong</h3>
        <p className="text-red-700">
          {componentName && `Error in ${componentName}: `}
          {error.message}
        </p>
      </div>
      
      <Button
        onClick={resetErrorBoundary}
        variant="outline"
        className="border-red-300 text-red-700 hover:bg-red-50"
        leftIcon={<ArrowPathIcon className="w-4 h-4" />}
      >
        Try Again
      </Button>
    </div>
  </div>
);

// Loading component with skeleton
const LoadingSpinner = ({ message = "Loading..." }) => (
  <div className="min-h-[400px] flex items-center justify-center p-8">
    <div className="text-center space-y-4">
      <div className="mx-auto w-12 h-12 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin" />
      <p className="text-gray-500 animate-pulse">{message}</p>
    </div>
  </div>
);

// Enhanced breadcrumb component
const Breadcrumb = ({ selectedCard, onNavigate }) => {
  const breadcrumbItems = useMemo(() => {
    const items = [{ label: 'Home', value: null, icon: HomeIcon }];
    
    if (selectedCard === 'template') {
      items.push({ 
        label: 'Template Generator', 
        value: 'template',
        icon: DocumentTextIcon 
      });
    } else if (selectedCard === 'testCases') {
      items.push({ 
        label: 'Test Case Generator', 
        value: 'testCases',
        icon: BeakerIcon 
      });
    }
    
    return items;
  }, [selectedCard]);

  return (
    <nav aria-label="Breadcrumb" className="mb-8">
      <ol className="flex items-center space-x-2 text-sm">
        {breadcrumbItems.map((item, index) => {
          const Icon = item.icon;
          const isLast = index === breadcrumbItems.length - 1;
          
          return (
            <li key={item.value || 'home'} className="flex items-center">
              {index > 0 && (
                <ChevronRightIcon className="w-4 h-4 text-gray-400 mx-2" />
              )}
              
              {isLast ? (
                <span className="flex items-center space-x-2 text-gray-900 font-medium">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </span>
              ) : (
                <button
                  onClick={() => onNavigate(item.value)}
                  className="flex items-center space-x-2 text-gray-500 hover:text-orange-600 transition-colors rounded-md px-2 py-1 hover:bg-orange-50"
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

// Feature cards data
const FEATURE_CARDS = [
  {
    id: 'template',
    title: 'Template Generator',
    description: 'Create and manage test case templates with customizable fields and validation rules.',
    icon: DocumentTextIcon,
    badge: 'Popular',
    gradient: 'from-orange-500 to-orange-600',
  },
  {
    id: 'testCases',
    title: 'Test Case Generator',
    description: 'Generate comprehensive test cases automatically from your requirements and specifications.',
    icon: BeakerIcon,
    badge: 'AI-Powered',
    gradient: 'from-orange-400 to-orange-500',
  },
  {
    id: 'settings',
    title: 'Settings & Configuration',
    description: 'Configure your testing environment, API endpoints, and generation preferences.',
    icon: CogIcon,
    badge: 'Coming Soon',
    gradient: 'from-gray-400 to-gray-500',
    disabled: true,
  },
];

const Home = () => {
  const [selectedCard, setSelectedCard] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle card selection with loading state
  const handleCardSelect = useCallback(async (cardType) => {
    if (cardType === 'settings') return; // Disabled card
    
    try {
      setError(null);
      setIsLoading(true);
      
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setSelectedCard(cardType);
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
    } catch (err) {
      setError(`Navigation error: ${err.message}`);
    }
  }, []);

  // Handle breadcrumb navigation
  const handleBreadcrumbNavigate = useCallback((value) => {
    try {
      setError(null);
      setSelectedCard(value);
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
  }, []);

  // Render current component
  const renderCurrentComponent = useMemo(() => {
    if (isLoading) {
      return <LoadingSpinner message="Loading component..." />;
    }

    if (error) {
      return (
        <div className="min-h-[400px] flex items-center justify-center p-8">
          <div className="max-w-md w-full text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-xl font-semibold text-red-900">Error</h3>
            <p className="text-red-700">{error}</p>
            <Button onClick={handleErrorRecovery} variant="outline">
              Return to Home
            </Button>
          </div>
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
            <div className="animate-fade-in">
              <TemplateForm onBack={handleBack} />
            </div>
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
            <div className="animate-fade-in">
              <TestCaseForm onBack={handleBack} />
            </div>
          </ErrorBoundary>
        );
      
      default:
        return (
          <ErrorBoundary
            FallbackComponent={(props) => 
              <ErrorFallback {...props} componentName="FeatureCards" />
            }
            onReset={handleErrorRecovery}
          >
            <div className="animate-fade-in space-y-8">
              {/* Hero Section */}
              <div className="text-center space-y-4 py-12">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-gradient-orange">
                  Test Case Generator
                </h1>
                <p className="text-lg md:text-xl leading-relaxed text-gray-600 max-w-2xl mx-auto">
                  Streamline your testing workflow with AI-powered test case generation, 
                  customizable templates, and intelligent automation tools.
                </p>
              </div>

              {/* Feature Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {FEATURE_CARDS.map((card) => {
                  const Icon = card.icon;
                  
                  return (
                    <FeatureCard
                      key={card.id}
                      title={card.title}
                      description={card.description}
                      icon={<Icon className="w-6 h-6" />}
                      badge={card.badge}
                      onClick={() => handleCardSelect(card.id)}
                      disabled={card.disabled}
                      className={cn(
                        'group relative overflow-hidden',
                        'hover:shadow-orange-lg transition-all duration-300',
                        'border border-orange-100 hover:border-orange-200',
                        card.disabled && 'opacity-60 cursor-not-allowed'
                      )}
                    />
                  );
                })}
              </div>

              {/* Stats Section */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-8">
                <div className="text-center space-y-2 p-6 bg-white rounded-xl shadow-orange border border-orange-100">
                  <div className="text-3xl font-bold text-orange-600">1000+</div>
                  <div className="text-sm text-gray-500">Test Cases Generated</div>
                </div>
                <div className="text-center space-y-2 p-6 bg-white rounded-xl shadow-orange border border-orange-100">
                  <div className="text-3xl font-bold text-orange-600">95%</div>
                  <div className="text-sm text-gray-500">Accuracy Rate</div>
                </div>
                <div className="text-center space-y-2 p-6 bg-white rounded-xl shadow-orange border border-orange-100">
                  <div className="text-3xl font-bold text-orange-600">50+</div>
                  <div className="text-sm text-gray-500">Templates Available</div>
                </div>
              </div>
            </div>
          </ErrorBoundary>
        );
    }
  }, [selectedCard, isLoading, error, handleCardSelect, handleBack, handleErrorRecovery]);

  // If a form is selected, render it without the main layout
  if (selectedCard === 'template' || selectedCard === 'testCases') {
    return (
      <ErrorBoundary
        FallbackComponent={(props) => 
          <ErrorFallback {...props} componentName="Home" />
        }
        onReset={handleErrorRecovery}
      >
        {renderCurrentComponent}
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary
      FallbackComponent={(props) => 
        <ErrorFallback {...props} componentName="Home" />
      }
      onReset={handleErrorRecovery}
    >
      <div className="bg-gradient-to-br from-orange-50 via-white to-orange-50">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-r from-orange-50/50 to-orange-100/50 pointer-events-none" />
        
        <div className="relative">
          {/* Skip to content link for accessibility */}
          <a 
            href="#main-content" 
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50 bg-orange-600 text-white px-4 py-2 rounded-md"
          >
            Skip to main content
          </a>

          {/* Main container */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header with navigation */}
            <header className="mb-8">
              <Breadcrumb 
                selectedCard={selectedCard} 
                onNavigate={handleBreadcrumbNavigate} 
              />
            </header>

            {/* Main content area */}
            <main 
              id="main-content"
              className="focus:outline-none"
              tabIndex={-1}
            >
              {renderCurrentComponent}
            </main>

            {/* Footer */}
            <footer className="mt-16 pt-8 border-t border-orange-200">
              <div className="text-center text-sm text-gray-500">
                <p>
                  Use the cards above to navigate between different sections. 
                  Press <kbd className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-mono">ESC</kbd> to go back.
                </p>
                <p className="mt-2">
                  © 2024 Zenius Test Case Generator. Built with modern web technologies.
                </p>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default Home; 