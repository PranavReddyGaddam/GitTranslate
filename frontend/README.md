# Repository to Podcast - Frontend

A modern React application that allows users to convert GitHub repositories into engaging podcasts using AI.

## Features

- 🎨 Modern, clean UI using ShadCN components and TailwindCSS
- 📱 Responsive design that works on desktop and mobile
- 🎯 Input validation and user feedback
- ⚡ Real-time loading states and animations
- 🎵 Support for basic (~5 min) and in-depth (~10 min) podcast modes
- 🔗 Sample repository buttons for quick testing

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **ShadCN UI** components
- **Radix UI** for accessible primitives
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/
│   ├── ui/           # ShadCN UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   └── radio-group.tsx
│   └── RepoInputCard.tsx  # Main component
├── lib/
│   └── utils.ts      # Utility functions
├── App.tsx           # Main app component
├── main.tsx          # Entry point
└── index.css         # Global styles
```

## Components

### RepoInputCard

The main component that handles:
- Repository URL input
- Podcast mode selection (Basic/In-Depth)
- Sample repository buttons
- Form submission and validation

### UI Components

All ShadCN UI components are built with:
- TypeScript support
- Accessibility features
- Consistent styling
- Customizable variants

## API Integration

The app includes a placeholder `generatePodcast` function in `App.tsx`. To integrate with your backend:

1. Replace the placeholder function with actual API calls
2. Update the endpoint URL to match your backend
3. Handle different response states (success, error, loading)

Example:
```typescript
const response = await fetch('/api/generate-podcast', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ repoUrl, mode })
});
```

## Customization

### Styling

- Colors and themes can be customized in `src/index.css`
- Component variants are defined in each component file
- TailwindCSS classes can be extended in `tailwind.config.js`

### Adding New Features

1. Create new components in `src/components/`
2. Add new UI primitives in `src/components/ui/`
3. Update the main App component to include new functionality

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- Use TypeScript for all components
- Follow React best practices
- Use functional components with hooks
- Maintain accessibility standards

## License

This project is part of the GitTranslate repository.
