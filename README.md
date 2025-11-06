# AI Chatbot Application

A modern, feature-rich AI chatbot application built with Angular 17. This application provides a beautiful user interface for conversing with an AI assistant, complete with user authentication, conversation management, and a responsive design.

## Features

### 🔐 Authentication
- **Email/Password Login**: Secure login with email validation
- **Password Visibility Toggle**: Show/hide password for better UX
- **Google Sign-In Ready**: UI prepared for Google OAuth integration
- **Persistent Sessions**: User sessions saved in localStorage

### 💬 Chat Interface
- **Real-time Messaging**: Smooth, instant message delivery
- **Conversation History**: All conversations saved and accessible
- **Multiple Conversations**: Create and manage multiple chat sessions
- **Message Timestamps**: Track when messages were sent
- **Loading Indicators**: Visual feedback while AI is "thinking"
- **Auto-scroll**: Automatically scrolls to latest messages

### 🎨 Modern UI/UX
- **Beautiful Gradient Design**: Eye-catching purple gradient theme
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Smooth Animations**: Polished animations throughout the app
- **Dark Sidebar**: Professional dark-themed navigation
- **Collapsible Sidebar**: Save screen space when needed
- **Suggestion Chips**: Quick start prompts for new conversations

### 📱 User Experience
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line
- **Empty States**: Helpful guidance when no messages exist
- **User Profile Display**: Shows current user information
- **Conversation Titles**: Auto-generated from first message
- **Delete Conversations**: Remove unwanted conversations
- **Clear All**: Quickly reset all conversations

## Screenshots

### Login Page
Beautiful login interface with email authentication and Google sign-in option.

### Chat Interface
Modern chat UI with sidebar navigation and message history.

## Installation

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd Internship
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:4200`

## Usage

### First Time Login
1. Open the application in your browser
2. Enter any valid email address (e.g., `user@example.com`)
3. Enter a password (minimum 6 characters)
4. Click "Sign In" to access the chat

### Starting a Conversation
1. After logging in, you'll see the chat interface
2. Click on any suggestion chip or type your message in the input box
3. Press Enter or click the send button to send your message
4. The AI will respond with a simulated message

### Managing Conversations
- **New Chat**: Click the "New Chat" button in the sidebar
- **Switch Chats**: Click on any conversation in the sidebar
- **Delete Chat**: Hover over a conversation and click the trash icon
- **Clear All**: Use the "Clear all chats" button at the bottom of the sidebar

### Logging Out
Click the logout icon in the user profile section at the bottom of the sidebar.

## Project Structure

```
Internship/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── chat-area/          # Main chat interface
│   │   │   ├── login/              # Login page
│   │   │   ├── message-bubble/     # Individual message display
│   │   │   └── sidebar/            # Navigation sidebar
│   │   ├── guards/
│   │   │   └── auth.guard.ts       # Route protection
│   │   ├── models/
│   │   │   └── message.model.ts    # Data models
│   │   ├── services/
│   │   │   ├── auth.service.ts     # Authentication logic
│   │   │   └── chat.service.ts     # Chat management
│   │   ├── app.component.ts        # Root component
│   │   ├── app.config.ts           # App configuration
│   │   └── app.routes.ts           # Routing configuration
│   ├── assets/                     # Static assets
│   ├── index.html                  # HTML entry point
│   ├── main.ts                     # Application bootstrap
│   └── styles.css                  # Global styles
├── angular.json                    # Angular configuration
├── package.json                    # Dependencies
└── tsconfig.json                   # TypeScript configuration
```

## Technology Stack

- **Framework**: Angular 17 (Standalone Components)
- **Language**: TypeScript 5.2
- **Styling**: CSS3 with custom properties
- **State Management**: Angular Signals
- **Routing**: Angular Router with Guards
- **Storage**: localStorage for persistence
- **Fonts**: Google Fonts (Inter)

## Key Features Explained

### Authentication Service
The `AuthService` handles user authentication with simple email/password validation. In a production environment, this should be connected to a real backend API.

### Chat Service
The `ChatService` manages all chat functionality:
- Creates and manages conversations
- Handles message sending and receiving
- Persists data to localStorage
- Simulates AI responses (ready for real API integration)

### Route Guards
The `authGuard` protects the chat routes, ensuring only authenticated users can access the chat interface.

## Customization

### Connecting to a Real AI API

To connect this chatbot to a real AI service (OpenAI, Anthropic, Google AI, etc.):

1. Open `src/app/services/chat.service.ts`
2. Find the `generateResponse()` method
3. Replace the simulated response with an actual API call:

```typescript
private async generateResponse(userMessage: string): Promise<string> {
  const response = await fetch('YOUR_AI_API_ENDPOINT', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: JSON.stringify({
      message: userMessage,
      // Add other required parameters
    })
  });
  
  const data = await response.json();
  return data.response;
}
```

### Styling Customization

The application uses CSS custom properties for easy theming. Key colors can be modified in the component stylesheets:

- Primary gradient: `#667eea` → `#764ba2`
- Secondary gradient: `#f093fb` → `#f5576c`
- Background: `#f7fafc`
- Dark background: `#1a202c`

## Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is available for educational and personal use.

## Support

For questions or issues, please refer to the documentation files:
- `SETUP_GUIDE.md` - Detailed setup instructions
- `FEATURES.md` - Complete feature documentation
- `CHANGELOG.md` - Version history and updates

## Acknowledgments

- Built with Angular 17
- Icons: Custom SVG icons
- Fonts: Inter by Google Fonts
- Inspiration: Modern AI chat interfaces

---

**Made with ❤️ using Angular**
