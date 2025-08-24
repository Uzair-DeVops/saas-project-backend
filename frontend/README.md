# VideoSaaS Frontend

A modern Next.js frontend for the VideoSaaS platform - a comprehensive video management and YouTube automation system.

## Features

- 🎥 **Video Management**: Upload, organize, and manage video content
- 📊 **Analytics Dashboard**: Track performance and engagement metrics
- 🤖 **AI-Powered Tools**: Generate titles, descriptions, and thumbnails
- 📺 **YouTube Integration**: Automated uploads with custom metadata
- 📋 **Playlist Management**: Create and manage YouTube playlists
- ⏰ **Scheduling**: Schedule video uploads and publishing
- 🔐 **Authentication**: Secure user authentication and authorization
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom component library with Lucide React icons
- **State Management**: React Context + Hooks
- **HTTP Client**: Axios
- **Forms**: React Hook Form with Zod validation
- **Notifications**: React Hot Toast
- **File Upload**: React Dropzone
- **Charts**: Recharts
- **Animations**: Framer Motion

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

## Installation

1. **Clone the repository** (if not already done):

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**:

   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── login/            # Authentication pages
│   │   ├── signup/
│   │   ├── globals.css       # Global styles
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Landing page
│   ├── components/           # Reusable components
│   │   ├── layout/          # Layout components
│   │   ├── providers/       # Context providers
│   │   └── ui/              # UI components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities and configurations
│   ├── types/               # TypeScript type definitions
│   └── utils/               # Helper functions
├── public/                  # Static assets
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

## Key Components

### Authentication

- **AuthProvider**: Manages user authentication state
- **useAuth Hook**: Provides authentication methods
- **Login/Signup Pages**: User authentication forms

### Dashboard

- **DashboardLayout**: Main layout with sidebar navigation
- **Dashboard Page**: Overview with statistics and charts
- **Upload Page**: Video upload with drag & drop

### API Integration

- **apiClient**: Centralized API client with interceptors
- **Type Definitions**: Full TypeScript support for API responses

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Integration

The frontend communicates with your FastAPI backend through the following endpoints:

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration
- `GET /api/auth/me` - Get current user

### Videos

- `POST /api/videos/upload` - Upload video file
- `POST /api/videos/download` - Download video from URL
- `GET /api/videos/my-videos` - Get user's videos

### Dashboard

- `GET /api/dashboard/overview` - Dashboard overview
- `GET /api/dashboard/playlists` - User's playlists
- `GET /api/dashboard/videos` - User's videos with analytics

### Content Generation

- `POST /api/title-generator/generate` - Generate video title
- `POST /api/description-generator/generate` - Generate description
- `POST /api/thumbnail-generator/generate` - Generate thumbnail

### YouTube Integration

- `POST /api/youtube-upload/{video_id}/upload` - Upload to YouTube
- `GET /api/youtube-token` - Get YouTube tokens
- `POST /api/youtube-token` - Create YouTube token

## Features Overview

### 1. Landing Page

- Modern, responsive design
- Feature highlights
- Call-to-action buttons
- User testimonials section

### 2. Authentication

- Login and signup forms
- Form validation
- Error handling
- Remember me functionality
- Google OAuth (placeholder)

### 3. Dashboard

- Overview statistics
- Recent videos and playlists
- Quick action buttons
- Performance metrics

### 4. Video Upload

- Drag & drop file upload
- URL-based video download
- Upload progress tracking
- File validation
- Multiple format support

### 5. Video Management

- Video listing with filters
- Video details and editing
- Status tracking
- YouTube upload integration

### 6. Analytics

- Performance metrics
- Engagement statistics
- Chart visualizations
- Export capabilities

### 7. AI Tools

- Title generation
- Description generation
- Thumbnail generation
- Timestamp generation

### 8. Settings

- User profile management
- API key configuration
- YouTube token management
- Privacy settings

## Styling

The project uses Tailwind CSS with a custom design system:

- **Primary Colors**: Blue palette for main actions
- **Secondary Colors**: Gray palette for text and backgrounds
- **Components**: Custom UI components with consistent styling
- **Responsive**: Mobile-first responsive design
- **Dark Mode**: Ready for dark mode implementation

## Development

### Adding New Pages

1. Create a new folder in `src/app/`
2. Add a `page.tsx` file
3. Use the `DashboardLayout` component for dashboard pages
4. Add navigation items to the sidebar

### Adding New Components

1. Create components in `src/components/`
2. Use TypeScript interfaces for props
3. Follow the existing component patterns
4. Add proper error handling

### API Integration

1. Add new endpoints to `src/lib/api.ts`
2. Create TypeScript interfaces in `src/types/`
3. Use the `apiClient` for all API calls
4. Handle loading and error states

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables
3. Deploy automatically on push

### Other Platforms

1. Build the project: `npm run build`
2. Start the production server: `npm run start`
3. Configure your hosting platform

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the code examples

## Roadmap

- [ ] Dark mode support
- [ ] Advanced analytics
- [ ] Team collaboration features
- [ ] Mobile app
- [ ] Advanced AI features
- [ ] Multi-language support
- [ ] Advanced scheduling
- [ ] Bulk operations
- [ ] API rate limiting
- [ ] Advanced security features
