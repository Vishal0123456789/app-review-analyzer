# Modern React Frontend for App Review Insights Analyzer

A professional, responsive React application built with **React 18**, **Tailwind CSS**, and **Vite**.

## Features

✨ **Modern Design**
- Clean, professional UI with gradient backgrounds
- Fully responsive (mobile-first approach)
- Smooth animations and transitions
- Card-based layout

📱 **Responsive**
- Mobile: Full-width with padding, single-column layout
- Tablet: Adaptive spacing and sizing
- Desktop: Centered card layout

🎯 **User-Friendly**
- Real-time form validation
- Loading spinner during analysis
- Clear status messages
- Accessible inputs and buttons

## Setup & Installation

### Prerequisites
- Node.js 16+ (download from https://nodejs.org/)
- npm or yarn

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at **http://localhost:5173** (proxies API calls to http://localhost:8000)

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx           # Main React component
│   ├── App.css           # Tailwind CSS setup
│   └── main.tsx          # React entry point
├── index.html            # HTML template
├── package.json          # Dependencies
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── postcss.config.js     # PostCSS configuration
└── tsconfig.json         # TypeScript configuration
```

## How It Works

1. **User enters window days** (7-56) and optional email
2. **Clicks "Analyze"** to trigger API call
3. **Loading spinner** shows while analysis runs
4. **Results display** with:
   - Date range
   - Top themes with summary bullets
   - Key quotes
   - Action ideas
   - Detailed notes
5. **Download button** to export pulse as JSON

## API Integration

The frontend communicates with the backend at http://localhost:8000:

- `POST /api/analyze` - Submit analysis request
- `GET /api/download-pulse?file=...` - Download pulse file

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **Vite** - Fast build tool
- **PostCSS** - CSS processing

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Tips

### Hot Reload
Changes to `src/**/*.tsx` automatically refresh the browser.

### TypeScript Errors
The editor will show TypeScript errors. Run:
```bash
npm run lint
```

### Styling
All styling uses Tailwind CSS classes. Modify colors, spacing, etc. in `tailwind.config.js`.

## Production Deployment

To use with the existing backend:

1. Build the React app:
   ```bash
   npm run build
   ```

2. The built files go to `dist/`

3. Update the backend to serve these static files instead of the old HTML

## Troubleshooting

**"Cannot find module 'react'"**
- Run `npm install` to install dependencies

**Port 5173 already in use**
- Change port in `vite.config.ts`:
  ```ts
  server: {
    port: 3000
  }
  ```

**API calls failing**
- Ensure backend is running on http://localhost:8000
- Check CORS is enabled in `app.py`

**Tailwind styles not applying**
- Run `npm run build` to rebuild
- Clear browser cache (Ctrl+Shift+Delete)

## Next Steps

- Customize colors in `tailwind.config.js`
- Add more detail pages for theme analysis
- Implement charts/graphs with data visualization libraries
- Add PWA (Progressive Web App) support
- Deploy to Vercel, Netlify, or your server

## Support

Refer to:
- [React Docs](https://react.dev)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vite Docs](https://vitejs.dev)
