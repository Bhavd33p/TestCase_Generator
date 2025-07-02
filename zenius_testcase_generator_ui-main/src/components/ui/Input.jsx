import React, { forwardRef, useState } from 'react';
import { cn } from '../../utils/cn';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

const Input = forwardRef(({
  className,
  type = 'text',
  error,
  success,
  helperText,
  label,
  placeholder,
  leftIcon,
  rightIcon,
  disabled = false,
  required = false,
  fullWidth = false,
  size = 'default',
  variant = 'default',
  ...props
}, ref) => {
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(false);

  const isPassword = type === 'password';
  const inputType = isPassword && showPassword ? 'text' : type;

  const sizeClasses = {
    sm: 'h-8 px-2 text-sm',
    default: 'h-10 px-3 text-sm',
    lg: 'h-12 px-4 text-base',
  };

  const variantClasses = {
    default: 'border-input bg-background',
    filled: 'border-transparent bg-muted',
    flushed: 'border-0 border-b-2 border-input bg-transparent rounded-none px-0',
  };

  const getStateClasses = () => {
    if (error) {
      return 'border-error-500 focus-visible:ring-error-500 text-error-900';
    }
    if (success) {
      return 'border-success-500 focus-visible:ring-success-500 text-success-900';
    }
    return 'border-input focus-visible:ring-ring';
  };

  const inputClasses = cn(
    'flex w-full rounded-md border bg-background text-foreground ring-offset-background transition-all duration-200',
    'file:border-0 file:bg-transparent file:text-sm file:font-medium',
    'placeholder:text-muted-foreground',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
    sizeClasses[size],
    variantClasses[variant],
    getStateClasses(),
    fullWidth ? 'w-full' : '',
    (leftIcon || rightIcon || isPassword) && 'pr-10',
    leftIcon && 'pl-10',
    className
  );

  return (
    <div className={cn('space-y-2', fullWidth && 'w-full')}>
      {label && (
        <label className={cn(
          'form-label',
          error && 'text-error-700',
          success && 'text-success-700',
          disabled && 'opacity-50'
        )}>
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {leftIcon}
          </div>
        )}
        
        <input
          type={inputType}
          className={inputClasses}
          ref={ref}
          disabled={disabled}
          placeholder={placeholder}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={helperText ? `${props.id}-helper` : undefined}
          {...props}
        />
        
        {(rightIcon || isPassword) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {isPassword ? (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded"
                tabIndex={-1}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeSlashIcon className="h-4 w-4" />
                ) : (
                  <EyeIcon className="h-4 w-4" />
                )}
              </button>
            ) : (
              <div className="text-muted-foreground">
                {rightIcon}
              </div>
            )}
          </div>
        )}
        
        {/* Focus ring for flushed variant */}
        {variant === 'flushed' && focused && (
          <div className={cn(
            'absolute bottom-0 left-0 right-0 h-0.5 rounded-full transition-all duration-200',
            error ? 'bg-error-500' : success ? 'bg-success-500' : 'bg-primary'
          )} />
        )}
      </div>
      
      {helperText && (
        <p
          id={`${props.id}-helper`}
          className={cn(
            'text-xs',
            error ? 'text-error-600' : success ? 'text-success-600' : 'text-muted-foreground'
          )}
        >
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Textarea component
const Textarea = forwardRef(({
  className,
  error,
  success,
  helperText,
  label,
  placeholder,
  disabled = false,
  required = false,
  fullWidth = false,
  rows = 4,
  resize = 'vertical',
  ...props
}, ref) => {
  const getStateClasses = () => {
    if (error) {
      return 'border-error-500 focus-visible:ring-error-500 text-error-900';
    }
    if (success) {
      return 'border-success-500 focus-visible:ring-success-500 text-success-900';
    }
    return 'border-input focus-visible:ring-ring';
  };

  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize',
  };

  const textareaClasses = cn(
    'form-textarea',
    getStateClasses(),
    resizeClasses[resize],
    fullWidth ? 'w-full' : '',
    className
  );

  return (
    <div className={cn('space-y-2', fullWidth && 'w-full')}>
      {label && (
        <label className={cn(
          'form-label',
          error && 'text-error-700',
          success && 'text-success-700',
          disabled && 'opacity-50'
        )}>
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        className={textareaClasses}
        ref={ref}
        disabled={disabled}
        placeholder={placeholder}
        rows={rows}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={helperText ? `${props.id}-helper` : undefined}
        {...props}
      />
      
      {helperText && (
        <p
          id={`${props.id}-helper`}
          className={cn(
            'text-xs',
            error ? 'text-error-600' : success ? 'text-success-600' : 'text-muted-foreground'
          )}
        >
          {helperText}
        </p>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

// Select component
const Select = forwardRef(({
  className,
  error,
  success,
  helperText,
  label,
  placeholder = 'Select an option...',
  disabled = false,
  required = false,
  fullWidth = false,
  children,
  ...props
}, ref) => {
  const getStateClasses = () => {
    if (error) {
      return 'border-error-500 focus-visible:ring-error-500';
    }
    if (success) {
      return 'border-success-500 focus-visible:ring-success-500';
    }
    return 'border-input focus-visible:ring-ring';
  };

  const selectClasses = cn(
    'flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:cursor-not-allowed disabled:opacity-50',
    'appearance-none bg-no-repeat bg-right bg-[length:16px_16px] pr-8',
    getStateClasses(),
    fullWidth ? 'w-full' : '',
    className
  );

  return (
    <div className={cn('space-y-2', fullWidth && 'w-full')}>
      {label && (
        <label className={cn(
          'form-label',
          error && 'text-error-700',
          success && 'text-success-700',
          disabled && 'opacity-50'
        )}>
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <select
          className={selectClasses}
          ref={ref}
          disabled={disabled}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={helperText ? `${props.id}-helper` : undefined}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {children}
        </select>
        
        {/* Custom dropdown arrow */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg
            className="h-4 w-4 text-muted-foreground"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>
      
      {helperText && (
        <p
          id={`${props.id}-helper`}
          className={cn(
            'text-xs',
            error ? 'text-error-600' : success ? 'text-success-600' : 'text-muted-foreground'
          )}
        >
          {helperText}
        </p>
      )}
    </div>
  );
});

Select.displayName = 'Select';

export { Input, Textarea, Select }; 