import React, { createContext, useContext, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/cn';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon, 
  XCircleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline';

// Toast Context
const ToastContext = createContext();

// Toast Provider
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((toast) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = {
      id,
      ...toast,
      createdAt: Date.now(),
    };

    setToasts(prev => [...prev, newToast]);

    // Auto remove toast after duration
    if (toast.duration !== 0) {
      setTimeout(() => {
        removeToast(id);
      }, toast.duration || 5000);
    }

    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const removeAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast, removeAllToasts }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
};

// Hook to use toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  const { addToast, removeToast, removeAllToasts } = context;

  const toast = useCallback((options) => {
    if (typeof options === 'string') {
      return addToast({ message: options, type: 'default' });
    }
    return addToast(options);
  }, [addToast]);

  toast.success = useCallback((message, options = {}) => {
    return addToast({ ...options, message, type: 'success' });
  }, [addToast]);

  toast.error = useCallback((message, options = {}) => {
    return addToast({ ...options, message, type: 'error' });
  }, [addToast]);

  toast.warning = useCallback((message, options = {}) => {
    return addToast({ ...options, message, type: 'warning' });
  }, [addToast]);

  toast.info = useCallback((message, options = {}) => {
    return addToast({ ...options, message, type: 'info' });
  }, [addToast]);

  toast.loading = useCallback((message, options = {}) => {
    return addToast({ ...options, message, type: 'loading', duration: 0 });
  }, [addToast]);

  toast.dismiss = removeToast;
  toast.dismissAll = removeAllToasts;

  return toast;
};

// Toast Container
const ToastContainer = ({ toasts, onRemove }) => {
  if (toasts.length === 0) return null;

  return createPortal(
    <div className="fixed top-4 right-4 z-50 flex flex-col space-y-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>,
    document.body
  );
};

// Individual Toast Component
const Toast = ({ toast, onRemove }) => {
  const { id, type, title, message, action, duration } = toast;

  const typeConfig = {
    default: {
      icon: InformationCircleIcon,
      className: 'bg-card border-border text-card-foreground',
    },
    success: {
      icon: CheckCircleIcon,
      className: 'bg-success-50 border-success-200 text-success-800',
    },
    error: {
      icon: XCircleIcon,
      className: 'bg-error-50 border-error-200 text-error-800',
    },
    warning: {
      icon: ExclamationTriangleIcon,
      className: 'bg-warning-50 border-warning-200 text-warning-800',
    },
    info: {
      icon: InformationCircleIcon,
      className: 'bg-primary-50 border-primary-200 text-primary-800',
    },
    loading: {
      icon: null,
      className: 'bg-card border-border text-card-foreground',
    },
  };

  const config = typeConfig[type] || typeConfig.default;
  const Icon = config.icon;

  return (
    <div
      className={cn(
        'relative flex items-start space-x-3 p-4 rounded-lg border shadow-lg',
        'animate-slide-in',
        config.className
      )}
      role="alert"
      aria-live="polite"
    >
      {/* Icon */}
      <div className="flex-shrink-0">
        {type === 'loading' ? (
          <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : Icon ? (
          <Icon className="w-5 h-5" />
        ) : null}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {title && (
          <p className="text-sm font-medium">{title}</p>
        )}
        <p className={cn('text-sm', title && 'mt-1')}>
          {message}
        </p>
        {action && (
          <div className="mt-2">
            {action}
          </div>
        )}
      </div>

      {/* Close button */}
      <button
        onClick={() => onRemove(id)}
        className="flex-shrink-0 p-1 rounded-md hover:bg-black/10 transition-colors"
        aria-label="Close notification"
      >
        <XMarkIcon className="w-4 h-4" />
      </button>

      {/* Progress bar for timed toasts */}
      {duration > 0 && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/10 rounded-b-lg overflow-hidden">
          <div 
            className="h-full bg-current opacity-50 animate-progress"
            style={{ 
              animation: `progress ${duration}ms linear forwards` 
            }}
          />
        </div>
      )}
    </div>
  );
};

// CSS for progress animation (add to your global styles)
const progressKeyframes = `
  @keyframes progress {
    from { width: 100%; }
    to { width: 0%; }
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = progressKeyframes;
  document.head.appendChild(style);
}

export { Toast, ToastContainer }; 