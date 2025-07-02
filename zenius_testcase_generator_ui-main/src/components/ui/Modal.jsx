import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/cn';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { Button } from './Button';

const Modal = ({
  isOpen,
  onClose,
  children,
  title,
  description,
  size = 'default',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
  overlayClassName,
  contentClassName,
  preventScroll = true,
  ...props
}) => {
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  const sizeClasses = {
    sm: 'max-w-md',
    default: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    '2xl': 'max-w-6xl',
    full: 'max-w-[95vw] max-h-[95vh]',
  };

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Handle focus management
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement;
      
      // Focus the modal after a brief delay to ensure it's rendered
      const timer = setTimeout(() => {
        if (modalRef.current) {
          modalRef.current.focus();
        }
      }, 100);

      return () => clearTimeout(timer);
    } else if (previousActiveElement.current) {
      previousActiveElement.current.focus();
    }
  }, [isOpen]);

  // Handle body scroll
  useEffect(() => {
    if (!preventScroll) return;

    if (isOpen) {
      const originalStyle = window.getComputedStyle(document.body).overflow;
      document.body.style.overflow = 'hidden';
      
      return () => {
        document.body.style.overflow = originalStyle;
      };
    }
  }, [isOpen, preventScroll]);

  // Handle focus trap
  const handleKeyDown = (event) => {
    if (event.key === 'Tab') {
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (!focusableElements?.length) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
  };

  const handleOverlayClick = (event) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  const modalContent = (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center p-4',
        'animate-fade-in',
        overlayClassName
      )}
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
      aria-describedby={description ? 'modal-description' : undefined}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-fade-in" />
      
      {/* Modal Content */}
      <div
        ref={modalRef}
        className={cn(
          'relative w-full bg-background rounded-xl shadow-hard border',
          'animate-scale-in',
          'focus:outline-none',
          'max-h-[90vh] overflow-hidden flex flex-col',
          sizeClasses[size],
          contentClassName,
          className
        )}
        tabIndex={-1}
        onKeyDown={handleKeyDown}
        {...props}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex-1">
              {title && (
                <h2 id="modal-title" className="text-xl font-semibold text-foreground">
                  {title}
                </h2>
              )}
              {description && (
                <p id="modal-description" className="mt-1 text-sm text-muted-foreground">
                  {description}
                </p>
              )}
            </div>
            
            {showCloseButton && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="ml-4 h-8 w-8 rounded-full"
                aria-label="Close modal"
              >
                <XMarkIcon className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
        
        {/* Content */}
        <div className="flex-1 overflow-auto">
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};

// Modal Header Component
const ModalHeader = ({ className, children, ...props }) => (
  <div
    className={cn('flex flex-col space-y-1.5 p-6 border-b', className)}
    {...props}
  >
    {children}
  </div>
);

// Modal Body Component
const ModalBody = ({ className, children, ...props }) => (
  <div className={cn('p-6', className)} {...props}>
    {children}
  </div>
);

// Modal Footer Component
const ModalFooter = ({ className, children, ...props }) => (
  <div
    className={cn(
      'flex items-center justify-end space-x-2 p-6 border-t bg-muted/30',
      className
    )}
    {...props}
  >
    {children}
  </div>
);

// Confirmation Modal Component
const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'default',
  loading = false,
  ...props
}) => {
  const variantStyles = {
    default: 'btn-primary',
    destructive: 'bg-error-600 hover:bg-error-700 text-white',
    warning: 'bg-warning-600 hover:bg-warning-700 text-white',
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      {...props}
    >
      <ModalBody>
        <p className="text-foreground">{message}</p>
      </ModalBody>
      
      <ModalFooter>
        <Button
          variant="outline"
          onClick={onClose}
          disabled={loading}
        >
          {cancelText}
        </Button>
        <Button
          className={variantStyles[variant]}
          onClick={onConfirm}
          loading={loading}
        >
          {confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

// Alert Modal Component
const AlertModal = ({
  isOpen,
  onClose,
  title = 'Alert',
  message,
  type = 'info',
  buttonText = 'OK',
  ...props
}) => {
  const typeStyles = {
    info: 'text-primary-600',
    success: 'text-success-600',
    warning: 'text-warning-600',
    error: 'text-error-600',
  };

  const typeIcons = {
    info: '💡',
    success: '✅',
    warning: '⚠️',
    error: '❌',
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center space-x-2">
          <span className="text-xl">{typeIcons[type]}</span>
          <span className={typeStyles[type]}>{title}</span>
        </div>
      }
      size="sm"
      {...props}
    >
      <ModalBody>
        <p className="text-foreground">{message}</p>
      </ModalBody>
      
      <ModalFooter>
        <Button onClick={onClose} className="w-full">
          {buttonText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

export {
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ConfirmationModal,
  AlertModal,
}; 