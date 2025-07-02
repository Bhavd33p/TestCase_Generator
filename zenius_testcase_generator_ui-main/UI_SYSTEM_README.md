# 🎨 Zenius UI System

A modern, scalable, and accessible UI component library built with React, Tailwind CSS, and TypeScript-ready patterns.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start
```

## 📦 Components Overview

### Core Components

#### Button (`/src/components/ui/Button.jsx`)
```jsx
import { Button } from './components/ui/Button';

// Basic usage
<Button>Click me</Button>

// With variants
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="ghost">Subtle</Button>

// With loading state
<Button loading>Processing...</Button>

// With icons
<Button leftIcon={<Icon />}>Save</Button>
```

**Props:**
- `variant`: default, destructive, outline, secondary, ghost, link, success, warning
- `size`: default, sm, lg, xl, icon
- `loading`: boolean
- `disabled`: boolean
- `fullWidth`: boolean
- `leftIcon`, `rightIcon`: React elements

#### Card System (`/src/components/ui/Card.jsx`)
```jsx
import { Card, CardHeader, CardTitle, CardContent, FeatureCard } from './components/ui/Card';

// Basic card
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
</Card>

// Feature card with interaction
<FeatureCard
  title="Feature Name"
  description="Feature description"
  icon={<Icon />}
  badge="New"
  onClick={handleClick}
/>
```

#### Form Components (`/src/components/ui/Input.jsx`)
```jsx
import { Input, Textarea, Select } from './components/ui/Input';

// Input with validation
<Input
  label="Email"
  type="email"
  error={errors.email}
  helperText="Enter your email address"
  required
/>

// Textarea
<Textarea
  label="Description"
  rows={4}
  placeholder="Enter description..."
/>

// Select
<Select label="Category">
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</Select>
```

#### Modal System (`/src/components/ui/Modal.jsx`)
```jsx
import { Modal, ConfirmationModal, AlertModal } from './components/ui/Modal';

// Basic modal
<Modal isOpen={isOpen} onClose={onClose} title="Modal Title">
  <p>Modal content</p>
</Modal>

// Confirmation modal
<ConfirmationModal
  isOpen={showConfirm}
  onClose={() => setShowConfirm(false)}
  onConfirm={handleConfirm}
  title="Delete Item"
  message="Are you sure you want to delete this item?"
  variant="destructive"
/>
```

#### Toast Notifications (`/src/components/ui/Toast.jsx`)
```jsx
import { useToast } from './components/ui/Toast';

function MyComponent() {
  const toast = useToast();
  
  const handleSuccess = () => {
    toast.success('Operation completed successfully!');
  };
  
  const handleError = () => {
    toast.error('Something went wrong');
  };
  
  return (
    <div>
      <Button onClick={handleSuccess}>Success</Button>
      <Button onClick={handleError}>Error</Button>
    </div>
  );
}
```

## 🎨 Design System

### Colors
The system uses a semantic color palette:
- **Primary**: Blue tones for main actions
- **Secondary**: Gray tones for secondary actions
- **Success**: Green tones for positive feedback
- **Warning**: Yellow/Orange tones for warnings
- **Error**: Red tones for errors and destructive actions

### Typography
- **Font Family**: Inter (primary), JetBrains Mono (monospace)
- **Scale**: Responsive typography with mobile-first approach
- **Weights**: 100-900 available

### Spacing
- **Base unit**: 0.25rem (4px)
- **Scale**: 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64

### Animations
- **Duration**: 150ms (fast), 200ms (normal), 300ms (slow)
- **Easing**: ease-out for entrances, ease-in for exits
- **Reduced motion**: Respects user preferences

## 🛠️ Utilities

### Class Name Utility (`/src/utils/cn.js`)
```jsx
import { cn } from './utils/cn';

// Combine classes conditionally
<div className={cn(
  'base-class',
  isActive && 'active-class',
  variant === 'primary' && 'primary-class'
)} />
```

### CSS Classes
```css
/* Layout */
.container, .container-sm, .container-md, .container-lg

/* Typography */
.heading-1, .heading-2, .heading-3, .heading-4
.body-large, .body-medium, .body-small
.text-gradient

/* Effects */
.glass, .glass-dark
.animate-fade-in, .animate-slide-up, .animate-scale-in

/* Status */
.status-success, .status-warning, .status-error, .status-info
```

## ♿ Accessibility Features

- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Screen Readers**: Proper ARIA labels and semantic HTML
- **Focus Management**: Visible focus indicators and logical tab order
- **Color Contrast**: WCAG AA compliant color combinations
- **Reduced Motion**: Respects user motion preferences
- **High Contrast**: Enhanced visibility for users with visual impairments

## 📱 Responsive Design

- **Mobile First**: Designed for mobile devices first
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Flexible Grid**: CSS Grid and Flexbox for layouts
- **Touch Friendly**: Appropriate touch targets (44px minimum)

## 🎯 Best Practices

### Component Usage
```jsx
// ✅ Good: Use semantic props
<Button variant="destructive" size="lg">
  Delete Account
</Button>

// ❌ Avoid: Custom styling that breaks the design system
<Button className="bg-red-500 text-white p-4">
  Delete Account
</Button>
```

### Error Handling
```jsx
// ✅ Good: Use ErrorBoundary for component isolation
<ErrorBoundary fallback={<ErrorFallback />}>
  <MyComponent />
</ErrorBoundary>

// ✅ Good: Provide meaningful error messages
toast.error('Failed to save changes. Please try again.');
```

### Loading States
```jsx
// ✅ Good: Show loading states for async operations
<Button loading={isSubmitting}>
  {isSubmitting ? 'Saving...' : 'Save Changes'}
</Button>
```

## 🔧 Customization

### Extending Components
```jsx
// Create custom variants
const CustomButton = ({ variant = 'custom', ...props }) => (
  <Button
    className={cn(
      variant === 'custom' && 'bg-purple-600 hover:bg-purple-700'
    )}
    {...props}
  />
);
```

### Theme Customization
Modify `tailwind.config.js` to customize:
- Colors
- Typography
- Spacing
- Animations
- Breakpoints

## 📚 Examples

### Form with Validation
```jsx
function ContactForm() {
  const [errors, setErrors] = useState({});
  const toast = useToast();
  
  const handleSubmit = async (data) => {
    try {
      await submitForm(data);
      toast.success('Form submitted successfully!');
    } catch (error) {
      toast.error('Failed to submit form');
    }
  };
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Contact Us</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          label="Name"
          error={errors.name}
          required
        />
        <Input
          label="Email"
          type="email"
          error={errors.email}
          required
        />
        <Textarea
          label="Message"
          error={errors.message}
          required
        />
        <Button type="submit" fullWidth>
          Send Message
        </Button>
      </CardContent>
    </Card>
  );
}
```

### Dashboard Layout
```jsx
function Dashboard() {
  return (
    <div className="container py-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <FeatureCard
          title="Analytics"
          description="View your analytics"
          icon={<ChartIcon />}
          onClick={() => navigate('/analytics')}
        />
        <FeatureCard
          title="Settings"
          description="Manage your settings"
          icon={<CogIcon />}
          onClick={() => navigate('/settings')}
        />
        <FeatureCard
          title="Profile"
          description="Update your profile"
          icon={<UserIcon />}
          onClick={() => navigate('/profile')}
        />
      </div>
    </div>
  );
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Styles not applying**: Ensure Tailwind CSS is properly configured
2. **Components not found**: Check import paths
3. **Animations not working**: Verify CSS imports
4. **TypeScript errors**: Add proper type definitions

### Performance Tips

1. **Lazy load components**: Use React.lazy for large components
2. **Memoize expensive operations**: Use useMemo and useCallback
3. **Optimize images**: Use appropriate formats and sizes
4. **Bundle analysis**: Use webpack-bundle-analyzer

## 📄 License

This UI system is part of the Zenius Test Case Generator project.

---

Built with ❤️ using React, Tailwind CSS, and modern web technologies. 