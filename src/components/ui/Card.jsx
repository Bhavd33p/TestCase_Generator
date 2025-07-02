import React, { forwardRef } from 'react';
import { cn } from '../../utils/cn';

const Card = forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-xl border bg-card text-card-foreground shadow-sm transition-all duration-200 hover:shadow-md',
      className
    )}
    {...props}
  />
));
Card.displayName = 'Card';

const CardHeader = forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('font-semibold leading-none tracking-tight', className)}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardDescription = forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

const CardContent = forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

// Interactive Card variant
const InteractiveCard = forwardRef(({ 
  className, 
  onClick, 
  selected = false, 
  disabled = false,
  children,
  ...props 
}, ref) => (
  <Card
    ref={ref}
    className={cn(
      'cursor-pointer transition-all duration-200',
      'hover:shadow-lg hover:scale-[1.02] hover:border-primary/50',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
      selected && 'border-primary bg-primary/5 shadow-md',
      disabled && 'cursor-not-allowed opacity-50 hover:shadow-sm hover:scale-100',
      className
    )}
    onClick={disabled ? undefined : onClick}
    tabIndex={disabled ? -1 : 0}
    role="button"
    aria-pressed={selected}
    onKeyDown={(e) => {
      if ((e.key === 'Enter' || e.key === ' ') && !disabled && onClick) {
        e.preventDefault();
        onClick(e);
      }
    }}
    {...props}
  >
    {children}
  </Card>
));
InteractiveCard.displayName = 'InteractiveCard';

// Feature Card with icon
const FeatureCard = forwardRef(({
  className,
  icon,
  title,
  description,
  onClick,
  selected = false,
  disabled = false,
  badge,
  ...props
}, ref) => (
  <InteractiveCard
    ref={ref}
    className={cn('relative overflow-hidden', className)}
    onClick={onClick}
    selected={selected}
    disabled={disabled}
    {...props}
  >
    {badge && (
      <div className="absolute top-4 right-4">
        <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
          {badge}
        </span>
      </div>
    )}
    
    <CardHeader className="pb-4">
      {icon && (
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
          {icon}
        </div>
      )}
      <CardTitle className="text-xl">{title}</CardTitle>
      {description && (
        <CardDescription className="mt-2 text-base leading-relaxed">
          {description}
        </CardDescription>
      )}
    </CardHeader>
  </InteractiveCard>
));
FeatureCard.displayName = 'FeatureCard';

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
  InteractiveCard,
  FeatureCard,
}; 