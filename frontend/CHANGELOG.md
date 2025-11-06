# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-11-04

### 🎉 Major Update - ChatGPT-Style Interface

#### Added
- **ChatGPT-like UI**: Complete redesign with professional interface
- **Sidebar Navigation**: Left sidebar for conversation management
- **Conversation History**: Support for multiple conversations
- **Dark Mode**: Full dark theme support with auto-detection
- **Markdown Rendering**: Rich text formatting in bot responses
- **Code Highlighting**: Syntax highlighting for 180+ languages
- **Copy Functionality**: One-click message copying
- **Suggested Prompts**: Quick-start prompt cards
- **Data Persistence**: LocalStorage for conversation history
- **Streaming Effect**: Typing indicators and cursor animation
- **Enhanced Database**: 10 products + 12 websites with detailed info
- **Better Search**: Improved keyword matching algorithm
- **Responsive Design**: Mobile-optimized layout

#### Components
- `SidebarComponent`: Conversation list and navigation
- `ChatAreaComponent`: Main chat interface with welcome screen
- `MessageBubbleComponent`: Individual message with actions
- `AIService`: Enhanced conversation management
- `MarkdownService`: Markdown parsing and rendering

#### UI Improvements
- Professional gradient-free design
- Smooth animations and transitions
- Better spacing and typography
- Hover effects and interactions
- Status indicators
- Time-based conversation grouping

#### Features
- Create new conversations
- Switch between conversations
- Delete individual conversations
- Clear all conversations
- Toggle dark/light theme
- Auto-save conversations
- Copy message content
- Format code with syntax highlighting
- Clickable links in responses
- Product cards with ratings and prices
- Website cards with features

### Changed
- **Architecture**: Migrated to conversation-based model
- **Styling**: New design system with CSS variables
- **Models**: Updated to support conversations
- **Services**: Refactored for better separation of concerns

### Technical
- Angular 17 standalone components
- TypeScript 5.2
- Marked.js for markdown
- Highlight.js for code
- RxJS for reactive state
- LocalStorage for persistence

---

## [1.0.0] - 2025-11-03

### Initial Release

#### Added
- Basic chatbot interface
- Simple product database (8 products)
- Basic website database (8 websites)
- Keyword-based search
- Direct links to products/websites
- Suggestion buttons
- Single conversation support
- Clear chat functionality
- Responsive design

#### Components
- `ChatComponent`: Main chat interface
- `MessageComponent`: Message display
- `ChatbotService`: Bot logic

#### Features
- Send messages
- Receive bot responses
- Product recommendations
- Website recommendations
- Basic keyword matching
- Auto-scroll to latest message

---

## Version Comparison

| Feature | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| Interface | Basic | ChatGPT-style |
| Conversations | Single | Multiple |
| Theme | Light only | Light + Dark |
| Markdown | No | Yes |
| Code Highlight | No | Yes |
| History | No | Yes (LocalStorage) |
| Copy Messages | No | Yes |
| Products | 8 | 10 |
| Websites | 8 | 12 |
| Sidebar | No | Yes |
| Persistence | No | Yes |

---

## Upgrade Guide (v1.0.0 → v2.0.0)

### Breaking Changes
- Component structure completely changed
- Service APIs updated
- Models restructured
- No backward compatibility with v1.0.0

### Migration Steps
1. Back up any custom modifications
2. Delete old `src/app/components/` directory
3. Install new dependencies: `npm install`
4. Copy new component files
5. Update any custom products/websites in `ai.service.ts`
6. Test thoroughly

### New Dependencies
```json
{
  "marked": "^9.1.0",
  "highlight.js": "^11.9.0"
}
```

---

## Future Roadmap

### v2.1.0 (Planned)
- [ ] Export conversations
- [ ] Search conversations
- [ ] Edit messages
- [ ] Regenerate responses

### v2.2.0 (Planned)
- [ ] Voice input/output
- [ ] Image support
- [ ] File uploads
- [ ] Rich media cards

### v3.0.0 (Future)
- [ ] Real AI integration (OpenAI API)
- [ ] User authentication
- [ ] Cloud sync
- [ ] Mobile app

---

## Notes

### Performance
- **v2.0.0**: Optimized rendering with OnPush strategy
- **LocalStorage**: Efficient conversation caching
- **Lazy Loading**: Components load on demand
- **Code Splitting**: Smaller initial bundle

### Security
- **XSS Protection**: Sanitized HTML rendering
- **Safe Links**: External links open in new tabs
- **Input Validation**: Prevented malicious input

### Accessibility
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: ARIA labels added
- **Color Contrast**: WCAG 2.1 AA compliant
- **Focus Indicators**: Clear focus states

---

*For detailed documentation, see README.md*


