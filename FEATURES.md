# FEATURES.md
## Angular Material Chat Application - Component Requirements

### Overview
Build a minimal, responsive real-time chat application using **Angular Material** + **Tailwind CSS**.

**⚠️ IMPORTANT: NO BACKEND CALLS**
- All data is **mocked** in services
- Authentication is **localStorage only**
- Messages persist in **localStorage only**
- No HTTP requests, no API calls, no WebSockets

**Tech Stack:**
- **Framework:** Angular 17+
- **UI:** Angular Material (components) + Tailwind CSS (layout/spacing)
- **Data:** Mock services only
- **Storage:** localStorage (users, messages, conversations)
- **Real-time:** Simulated with setTimeout (no actual real-time backend)

**Project Structure Philosophy:**
- Keep components **small and focused** (< 150 lines)
- Extract reusable UI into **sub-components**
- Use **smart/dumb component pattern**
- TODOs reference acceptance criteria from this doc

---

## Core Features

### 1. Login System
- Email/password authentication (mocked)
- User registration (optional)
- Session persistence (localStorage)
- Auto-login if session exists

### 2. Chat Interface
- Send/receive messages
- Message bubbles (sender/receiver styling)
- Timestamp display
- Auto-scroll to latest message
- Input field with send button

### 3. Multiple Conversations
- Create new conversations
- Switch between conversations
- Delete conversations
- Conversation list with last message preview

### 4. Sidebar Navigation
- List all conversations
- Active conversation highlighting
- User profile display
- Logout button

### 5. Responsive Design
- Mobile: Full-screen chat, collapsible sidebar
- Tablet/Desktop: Sidebar + chat side-by-side
- Tailwind breakpoints for layout

---

## Services Architecture

### AuthService (Mock Authentication)
**File:** `src/app/services/auth.service.ts`

**Purpose:** Handle user authentication with localStorage - NO BACKEND

**Acceptance Criteria:**
- [ ] AC-1.1: Store current user in localStorage (key: `'chat_current_user'`)
- [ ] AC-1.2: Mock user database in localStorage (key: `'chat_users'`)
- [ ] AC-1.3: User interface: `{ id, email, password, displayName, avatarUrl, createdAt }`
- [ ] AC-1.4: Method `login(email, password): Observable<User | null>` - validate credentials
- [ ] AC-1.5: Method `logout(): void` - clear current user from localStorage
- [ ] AC-1.6: Method `isAuthenticated(): boolean` - check if user is logged in
- [ ] AC-1.7: Method `getCurrentUser(): User | null` - get current user
- [ ] AC-1.8: Method `register(email, password, displayName): Observable<User | null>` - create new user
- [ ] AC-1.9: BehaviorSubject `currentUser$` for reactive auth state
- [ ] AC-1.10: Pre-populate with 2-3 demo users for testing

**TODO:**
```typescript
// TODO: AC-1.1 - Define CURRENT_USER_KEY = 'chat_current_user'
// TODO: AC-1.2 - Define USERS_DB_KEY = 'chat_users', seed with demo users
// TODO: AC-1.3 - Define User interface in models/user.model.ts
// TODO: AC-1.4 - Implement login() - find user, validate password, store in localStorage
// TODO: AC-1.5 - Implement logout() - remove from localStorage, emit null
// TODO: AC-1.6 - Implement isAuthenticated() - check if currentUser exists
// TODO: AC-1.7 - Implement getCurrentUser() - parse from localStorage
// TODO: AC-1.8 - Implement register() - check email uniqueness, add to users DB
// TODO: AC-1.9 - Create private currentUser$ = new BehaviorSubject<User | null>(null)
// TODO: AC-1.10 - Create seedDemoUsers() - add demo@example.com, user@example.com
```

---

### ChatService (Mock Real-time Chat)
**File:** `src/app/services/chat.service.ts`

**Purpose:** Manage conversations and messages with localStorage - NO BACKEND

**Acceptance Criteria:**
- [ ] AC-2.1: Store conversations in localStorage (key: `'chat_conversations'`)
- [ ] AC-2.2: Conversation interface: `{ id, participants, lastMessage, lastMessageTime, createdAt }`
- [ ] AC-2.3: Message interface: `{ id, conversationId, senderId, text, timestamp, read }`
- [ ] AC-2.4: Method `getConversations(userId): Observable<Conversation[]>` - get user's conversations
- [ ] AC-2.5: Method `getMessages(conversationId): Observable<Message[]>` - get conversation messages
- [ ] AC-2.6: Method `sendMessage(conversationId, senderId, text): void` - add message
- [ ] AC-2.7: Method `createConversation(currentUserId, otherUserId): Conversation` - create new chat
- [ ] AC-2.8: Method `deleteConversation(conversationId): void` - remove conversation
- [ ] AC-2.9: Method `simulateIncomingMessage(conversationId): void` - mock received messages
- [ ] AC-2.10: BehaviorSubject `conversations$` for reactive updates
- [ ] AC-2.11: BehaviorSubject `messages$` for reactive updates
- [ ] AC-2.12: Auto-save to localStorage on every change

**TODO:**
```typescript
// TODO: AC-2.1 - Define CONVERSATIONS_KEY = 'chat_conversations'
// TODO: AC-2.2 - Define Conversation interface in models/conversation.model.ts
// TODO: AC-2.3 - Define Message interface in models/message.model.ts
// TODO: AC-2.4 - Implement getConversations() - filter by userId in participants
// TODO: AC-2.5 - Implement getMessages() - filter messages by conversationId
// TODO: AC-2.6 - Implement sendMessage() - add message, update lastMessage, save
// TODO: AC-2.7 - Implement createConversation() - generate ID, add to conversations
// TODO: AC-2.8 - Implement deleteConversation() - filter out, save
// TODO: AC-2.9 - Implement simulateIncomingMessage() - setTimeout to add mock message
// TODO: AC-2.10 - Create private conversations$ = new BehaviorSubject<Conversation[]>([])
// TODO: AC-2.11 - Create private messages$ = new BehaviorSubject<Message[]>([])
// TODO: AC-2.12 - Call saveToLocalStorage() after mutations
```

---

### ContactsService (Mock Contacts)
**File:** `src/app/services/contacts.service.ts`

**Purpose:** Provide list of users to start conversations with - MOCK ONLY

**Acceptance Criteria:**
- [ ] AC-3.1: Return hardcoded list of demo users (5-10 users)
- [ ] AC-3.2: Method `getContacts(): Observable<User[]>` - get all users except current
- [ ] AC-3.3: Method `searchContacts(query): User[]` - filter by name/email

**TODO:**
```typescript
// TODO: AC-3.1 - Create mock users array (5-10 users with different avatars)
// TODO: AC-3.2 - Implement getContacts() - return users excluding current user
// TODO: AC-3.3 - Implement searchContacts() - filter by displayName or email
```

---

## Routing Configuration

### Routes Definition
```typescript
const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { 
    path: 'chat', 
    component: ChatLayoutComponent,
    canActivate: [AuthGuard],
    children: [
      { path: '', component: ConversationsListComponent },
      { path: ':conversationId', component: ChatWindowComponent }
    ]
  },
  { path: '**', redirectTo: '/login' }
];
```

**Acceptance Criteria:**
- [ ] AC-4.1: App redirects to /login if not authenticated
- [ ] AC-4.2: After login, navigate to /chat
- [ ] AC-4.3: /chat shows conversations list (no conversation selected)
- [ ] AC-4.4: /chat/:conversationId shows chat window for that conversation
- [ ] AC-4.5: AuthGuard prevents access to /chat if not logged in
- [ ] AC-4.6: Browser back/forward buttons work correctly

---

## Component 1: Login (Smart Component)

**Route:** `/login`  
**File:** `src/app/pages/login/login.component.ts`

**Purpose:** User authentication form (< 100 lines)

**Material:** mat-card, mat-form-field, mat-input, mat-button, mat-progress-spinner  
**Tailwind:** `flex items-center justify-center min-h-screen bg-gray-100`

### Acceptance Criteria

**LoginComponent:**
- [ ] AC-5.1: Check if already authenticated in ngOnInit, redirect to /chat
- [ ] AC-5.2: Reactive form with email and password fields
- [ ] AC-5.3: Validators: email (required, valid email), password (required, min 6 chars)
- [ ] AC-5.4: "Login" button disabled if form invalid
- [ ] AC-5.5: On submit, call AuthService.login()
- [ ] AC-5.6: Show loading spinner during login
- [ ] AC-5.7: On success, navigate to /chat
- [ ] AC-5.8: On failure, show error snackbar: "Invalid credentials"
- [ ] AC-5.9: Display demo credentials hint (email: demo@example.com, password: demo123)
- [ ] AC-5.10: Optional "Register" link (if registration implemented)

**TODO:**
```typescript
// login.component.ts (Smart Component - keep < 100 lines)
// TODO: AC-5.1 - Inject AuthService, check isAuthenticated(), navigate if true
// TODO: AC-5.2 - Create FormGroup with email and password controls
// TODO: AC-5.3 - Add Validators.required, Validators.email, Validators.minLength(6)
// TODO: AC-5.4 - [disabled]="loginForm.invalid || isLoading"
// TODO: AC-5.5 - onSubmit() calls authService.login(email, password).subscribe()
// TODO: AC-5.6 - Set isLoading = true before login, false after
// TODO: AC-5.7 - On success: router.navigate(['/chat'])
// TODO: AC-5.8 - On error: snackBar.open('Invalid credentials', 'Close')
// TODO: AC-5.9 - Display hint in template: "Demo: demo@example.com / demo123"
// TODO: AC-5.10 - Add register link (if implementing registration)
```

**Skeleton Code:**
```typescript
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  isLoading = false;
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }
  
  ngOnInit() {
    // TODO: AC-5.1
  }
  
  onSubmit() {
    // TODO: AC-5.5, AC-5.6, AC-5.7, AC-5.8
  }
}
```

---

## Component 2: Chat Layout (Smart Component)

**Route:** `/chat`  
**File:** `src/app/pages/chat-layout/chat-layout.component.ts`

**Purpose:** Main layout with sidebar + chat area (< 100 lines)

**Component Breakdown:**
- **Smart Component:** ChatLayoutComponent (manages layout state)
- **Dumb Components:**
  - `SidebarComponent` - navigation with conversations list
  - `ChatWindowComponent` - active chat messages

**Material:** mat-sidenav, mat-sidenav-container, mat-toolbar  
**Tailwind:** `h-screen flex`

### Acceptance Criteria

**ChatLayoutComponent:**
- [ ] AC-6.1: Use mat-sidenav-container for layout
- [ ] AC-6.2: Sidebar opened by default on desktop (> 1024px)
- [ ] AC-6.3: Sidebar collapsed on mobile (< 768px), toggle with button
- [ ] AC-6.4: Subscribe to AuthService.currentUser$ for user info
- [ ] AC-6.5: Display current user in toolbar (avatar + name)
- [ ] AC-6.6: Logout button in toolbar
- [ ] AC-6.7: Router outlet for chat content (ConversationsListComponent or ChatWindowComponent)

**TODO:**
```typescript
// chat-layout.component.ts (Smart Component - keep < 100 lines)
// TODO: AC-6.1 - Use mat-sidenav-container in template
// TODO: AC-6.2 - Set [opened]="isMobile ? false : true" based on screen size
// TODO: AC-6.3 - Add toggle button for mobile (mat-icon-button with menu icon)
// TODO: AC-6.4 - Subscribe to authService.currentUser$ in ngOnInit
// TODO: AC-6.5 - Display user.displayName and avatar in toolbar
// TODO: AC-6.6 - Add logout button: onClick calls authService.logout(), navigate to /login
// TODO: AC-6.7 - Add <router-outlet> for child routes
```

**Skeleton Code:**
```typescript
@Component({
  selector: 'app-chat-layout',
  templateUrl: './chat-layout.component.html',
  styleUrls: ['./chat-layout.component.scss']
})
export class ChatLayoutComponent implements OnInit {
  currentUser: User | null = null;
  isMobile = false;
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}
  
  ngOnInit() {
    // TODO: AC-6.4
    // TODO: AC-6.2 - Detect screen size
  }
  
  toggleSidebar() {
    // TODO: AC-6.3
  }
  
  logout() {
    // TODO: AC-6.6
  }
}
```

---

## Component 3: Sidebar (Dumb Component)

**File:** `src/app/components/sidebar/sidebar.component.ts`

**Purpose:** Display conversations list and user info (< 80 lines)

**Material:** mat-list, mat-list-item, mat-icon, mat-button, mat-divider  
**Tailwind:** `w-full md:w-80 h-full flex flex-col`

### Acceptance Criteria

**SidebarComponent:**
- [ ] AC-7.1: @Input() currentUser: User
- [ ] AC-7.2: @Input() conversations: Conversation[]
- [ ] AC-7.3: @Output() conversationSelected = new EventEmitter<string>()
- [ ] AC-7.4: @Output() newConversation = new EventEmitter<void>()
- [ ] AC-7.5: @Output() logout = new EventEmitter<void>()
- [ ] AC-7.6: Display user info at top (avatar, name)
- [ ] AC-7.7: "New Chat" button (emits newConversation event)
- [ ] AC-7.8: List all conversations (use *ngFor)
- [ ] AC-7.9: Each conversation shows: other user's name, last message preview, timestamp
- [ ] AC-7.10: Highlight active conversation (from route)
- [ ] AC-7.11: Click conversation emits conversationSelected with ID
- [ ] AC-7.12: Logout button at bottom

**TODO:**
```typescript
// sidebar.component.ts (Dumb Component - keep < 80 lines)
// TODO: AC-7.1 to AC-7.5 - Define inputs and outputs
// TODO: AC-7.6 - Template: display currentUser.displayName and avatarUrl
// TODO: AC-7.7 - "New Chat" button with mat-icon (add) - (click)="newConversation.emit()"
// TODO: AC-7.8 - mat-list with *ngFor="let conv of conversations"
// TODO: AC-7.9 - Display conv.lastMessage, conv.lastMessageTime | date
// TODO: AC-7.10 - [class.active]="conv.id === activeConversationId"
// TODO: AC-7.11 - (click)="conversationSelected.emit(conv.id)"
// TODO: AC-7.12 - Logout button: (click)="logout.emit()"
```

**Skeleton Code:**
```typescript
@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
  standalone: true,
  imports: [MaterialModules, CommonModule]
})
export class SidebarComponent {
  @Input() currentUser!: User;
  @Input() conversations: Conversation[] = [];
  @Input() activeConversationId?: string;
  @Output() conversationSelected = new EventEmitter<string>();
  @Output() newConversation = new EventEmitter<void>();
  @Output() logout = new EventEmitter<void>();
}
```

---

## Component 4: Conversations List (Smart Component)

**Route:** `/chat` (child route, default)  
**File:** `src/app/pages/conversations-list/conversations-list.component.ts`

**Purpose:** Show all conversations or prompt to start new chat (< 80 lines)

**Material:** mat-card, mat-button, mat-icon  
**Tailwind:** `flex items-center justify-center h-full`

### Acceptance Criteria

**ConversationsListComponent:**
- [ ] AC-8.1: Subscribe to ChatService.conversations$ in ngOnInit
- [ ] AC-8.2: If no conversations, show "No conversations yet" with "Start New Chat" button
- [ ] AC-8.3: If conversations exist, show "Select a conversation to start chatting"
- [ ] AC-8.4: "Start New Chat" opens dialog to select contact
- [ ] AC-8.5: On contact selected, create conversation, navigate to /chat/:conversationId

**TODO:**
```typescript
// conversations-list.component.ts (Smart Component - keep < 80 lines)
// TODO: AC-8.1 - Subscribe to chatService.conversations$
// TODO: AC-8.2 - *ngIf="conversations.length === 0" show empty state
// TODO: AC-8.3 - *ngIf="conversations.length > 0" show select prompt
// TODO: AC-8.4 - openNewChatDialog() opens MatDialog with ContactsListDialog
// TODO: AC-8.5 - On dialog result, call chatService.createConversation(), navigate
```

---

## Component 5: Chat Window (Smart Component)

**Route:** `/chat/:conversationId`  
**File:** `src/app/pages/chat-window/chat-window.component.ts`

**Purpose:** Display messages and input field (< 150 lines)

**Component Breakdown:**
- **Smart Component:** ChatWindowComponent (handles messages, sending)
- **Dumb Components:**
  - `MessageBubbleComponent` - single message display
  - `MessageInputComponent` - input field + send button

**Material:** mat-card, mat-form-field, mat-input, mat-button, mat-icon  
**Tailwind:** `flex flex-col h-full`

### Acceptance Criteria

**ChatWindowComponent:**
- [ ] AC-9.1: Get conversationId from route params
- [ ] AC-9.2: Subscribe to ChatService.messages$ filtered by conversationId
- [ ] AC-9.3: Load conversation details (other user's info)
- [ ] AC-9.4: Display other user's name in header
- [ ] AC-9.5: Display messages in scrollable area (auto-scroll to bottom)
- [ ] AC-9.6: Group messages by sender (consecutive messages)
- [ ] AC-9.7: Handle sendMessage event from MessageInputComponent
- [ ] AC-9.8: Call ChatService.sendMessage() with text
- [ ] AC-9.9: Simulate incoming message after 2-3 seconds (random mock response)
- [ ] AC-9.10: Show "Delete Conversation" button (with confirmation dialog)
- [ ] AC-9.11: Scroll to bottom when new message arrives
- [ ] AC-9.12: Show typing indicator (optional, simulated)

**TODO:**
```typescript
// chat-window.component.ts (Smart Component - keep < 150 lines)
// TODO: AC-9.1 - Get conversationId from ActivatedRoute
// TODO: AC-9.2 - Subscribe to chatService.messages$, filter by conversationId
// TODO: AC-9.3 - Get conversation from chatService.getConversations()
// TODO: AC-9.4 - Display otherUser.displayName in toolbar
// TODO: AC-9.5 - Messages container with overflow-y-auto, scroll to bottom
// TODO: AC-9.6 - Use *ngFor with consecutive message grouping logic
// TODO: AC-9.7 - onSendMessage(text: string) handler
// TODO: AC-9.8 - chatService.sendMessage(conversationId, currentUserId, text)
// TODO: AC-9.9 - setTimeout(() => chatService.simulateIncomingMessage(conversationId), 2000)
// TODO: AC-9.10 - deleteConversation() with MatDialog confirmation
// TODO: AC-9.11 - Use ViewChild to access messages container, scrollIntoView()
// TODO: AC-9.12 - Show "typing..." indicator (optional)
```

**Skeleton Code:**
```typescript
@Component({
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.scss']
})
export class ChatWindowComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer?: ElementRef;
  
  conversationId!: string;
  messages: Message[] = [];
  currentUser!: User;
  otherUser?: User;
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private chatService: ChatService,
    private authService: AuthService,
    private dialog: MatDialog
  ) {}
  
  ngOnInit() {
    // TODO: AC-9.1, AC-9.2, AC-9.3, AC-9.4
  }
  
  ngAfterViewChecked() {
    // TODO: AC-9.11 - Scroll to bottom
  }
  
  onSendMessage(text: string) {
    // TODO: AC-9.7, AC-9.8, AC-9.9
  }
  
  deleteConversation() {
    // TODO: AC-9.10
  }
}
```

---

## Component 6: Message Bubble (Dumb Component)

**File:** `src/app/components/message-bubble/message-bubble.component.ts`

**Purpose:** Display single message with styling (< 40 lines)

**Material:** mat-card (or custom div)  
**Tailwind:** `flex mb-2`, sender: `justify-end`, receiver: `justify-start`

### Acceptance Criteria

**MessageBubbleComponent:**
- [ ] AC-10.1: @Input() message: Message
- [ ] AC-10.2: @Input() isSender: boolean (true if current user sent it)
- [ ] AC-10.3: Display message text
- [ ] AC-10.4: Display timestamp (formatted: HH:mm)
- [ ] AC-10.5: Sender messages: right-aligned, blue background
- [ ] AC-10.6: Receiver messages: left-aligned, gray background
- [ ] AC-10.7: Rounded corners, padding, max-width

**TODO:**
```typescript
// message-bubble.component.ts (Dumb Component - keep < 40 lines)
// TODO: AC-10.1, AC-10.2 - Define inputs
// TODO: AC-10.3 - Display message.text
// TODO: AC-10.4 - Display message.timestamp | date:'HH:mm'
// TODO: AC-10.5 - [class.sender]="isSender" with Tailwind: bg-blue-500 text-white ml-auto
// TODO: AC-10.6 - [class.receiver]="!isSender" with Tailwind: bg-gray-200 text-black mr-auto
// TODO: AC-10.7 - Tailwind: rounded-lg p-3 max-w-xs
```

**Skeleton Code:**
```typescript
@Component({
  selector: 'app-message-bubble',
  template: `
    <div class="flex mb-2" [class.justify-end]="isSender" [class.justify-start]="!isSender">
      <!-- TODO: AC-10.3 to AC-10.7 -->
    </div>
  `,
  standalone: true,
  imports: [CommonModule]
})
export class MessageBubbleComponent {
  @Input() message!: Message;
  @Input() isSender = false;
}
```

---

## Component 7: Message Input (Dumb Component)

**File:** `src/app/components/message-input/message-input.component.ts`

**Purpose:** Input field + send button (< 50 lines)

**Material:** mat-form-field, mat-input, mat-button, mat-icon  
**Tailwind:** `flex gap-2 p-4 border-t`

### Acceptance Criteria

**MessageInputComponent:**
- [ ] AC-11.1: @Output() sendMessage = new EventEmitter<string>()
- [ ] AC-11.2: Input field for message text (not a form, just ngModel)
- [ ] AC-11.3: Send button (mat-icon-button with send icon)
- [ ] AC-11.4: Send button disabled if input is empty
- [ ] AC-11.5: On send, emit message text, clear input
- [ ] AC-11.6: Handle Enter key to send (Shift+Enter for new line)
- [ ] AC-11.7: Focus input field on component load

**TODO:**
```typescript
// message-input.component.ts (Dumb Component - keep < 50 lines)
// TODO: AC-11.1 - Define output
// TODO: AC-11.2 - [(ngModel)]="messageText"
// TODO: AC-11.3 - mat-icon-button with (click)="onSend()"
// TODO: AC-11.4 - [disabled]="!messageText.trim()"
// TODO: AC-11.5 - onSend() emits messageText, sets messageText = ''
// TODO: AC-11.6 - (keydown.enter)="onSend()" with event.preventDefault()
// TODO: AC-11.7 - Use ViewChild + focus() in ngAfterViewInit
```

**Skeleton Code:**
```typescript
@Component({
  selector: 'app-message-input',
  templateUrl: './message-input.component.html',
  styleUrls: ['./message-input.component.scss'],
  standalone: true,
  imports: [MaterialModules, FormsModule]
})
export class MessageInputComponent implements AfterViewInit {
  @ViewChild('messageInput') messageInput?: ElementRef;
  @Output() sendMessage = new EventEmitter<string>();
  messageText = '';
  
  ngAfterViewInit() {
    // TODO: AC-11.7
  }
  
  onSend() {
    // TODO: AC-11.5
  }
  
  onEnterKey(event: KeyboardEvent) {
    // TODO: AC-11.6
  }
}
```

---

## Component 8: New Chat Dialog (Smart Component)

**File:** `src/app/components/new-chat-dialog/new-chat-dialog.component.ts`

**Purpose:** Select contact to start new conversation (< 80 lines)

**Material:** mat-dialog, mat-list, mat-list-item, mat-form-field, mat-input  
**Tailwind:** `w-96 max-h-96 overflow-auto`

### Acceptance Criteria

**NewChatDialogComponent:**
- [ ] AC-12.1: Inject ContactsService to get contacts
- [ ] AC-12.2: Load all contacts on init (exclude current user)
- [ ] AC-12.3: Search bar to filter contacts by name
- [ ] AC-12.4: Display contacts in mat-list
- [ ] AC-12.5: Show avatar, name, email for each contact
- [ ] AC-12.6: On contact click, close dialog with selected user
- [ ] AC-12.7: "Cancel" button to close without selection

**TODO:**
```typescript
// new-chat-dialog.component.ts (Smart Component - keep < 80 lines)
// TODO: AC-12.1 - Inject ContactsService
// TODO: AC-12.2 - Load contacts in ngOnInit, filter out currentUser
// TODO: AC-12.3 - Search input with (input)="filterContacts($event)"
// TODO: AC-12.4 - mat-list with *ngFor="let contact of filteredContacts"
// TODO: AC-12.5 - Display contact.avatarUrl, contact.displayName, contact.email
// TODO: AC-12.6 - (click)="selectContact(contact)" calls dialogRef.close(contact)
// TODO: AC-12.7 - Cancel button: dialogRef.close(null)
```

---

## Data Models

### User Interface
```typescript
// models/user.model.ts
export interface User {
  id: string;
  email: string;
  password?: string;  // Only in localStorage, never exposed in UI
  displayName: string;
  avatarUrl?: string;
  createdAt: string;
}
```

### Conversation Interface
```typescript
// models/conversation.model.ts
export interface Conversation {
  id: string;
  participants: string[];  // Array of user IDs
  lastMessage: string;
  lastMessageTime: string; // ISO string
  createdAt: string;
}
```

### Message Interface
```typescript
// models/message.model.ts
export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  text: string;
  timestamp: string;      // ISO string
  read: boolean;
}
```

---

## Mock Data Structure

### Demo Users (AuthService)
```typescript
const DEMO_USERS: User[] = [
  {
    id: '1',
    email: 'demo@example.com',
    password: 'demo123',
    displayName: 'Demo User',
    avatarUrl: 'https://i.pravatar.cc/150?img=1',
    createdAt: new Date().toISOString()
  },
  {
    id: '2',
    email: 'user@example.com',
    password: 'user123',
    displayName: 'John Doe',
    avatarUrl: 'https://i.pravatar.cc/150?img=2',
    createdAt: new Date().toISOString()
  },
  {
    id: '3',
    email: 'alice@example.com',
    password: 'alice123',
    displayName: 'Alice Smith',
    avatarUrl: 'https://i.pravatar.cc/150?img=3',
    createdAt: new Date().toISOString()
  }
];
```

### Mock Contacts (ContactsService)
```typescript
// 5-10 demo users for starting conversations
const MOCK_CONTACTS: User[] = [
  // Same as DEMO_USERS + additional users
];
```

### Mock Incoming Messages (ChatService)
```typescript
// Random responses for simulating incoming messages
const MOCK_RESPONSES = [
  "Hey! How are you?",
  "That's interesting!",
  "Let me think about that...",
  "Sure, sounds good!",
  "I'll get back to you soon.",
  "Thanks for letting me know!",
  "😊",
  "What do you think?",
  "Absolutely!",
  "I'm not sure about that."
];
```

---

## Styling Guidelines

### Material Theme
- [ ] Use default Material theme or custom primary/accent colors
- [ ] Consistent button styles (primary for send, secondary for cancel)
- [ ] Use Material elevation for cards/sidebar

### Tailwind Utilities
- [ ] Use Tailwind ONLY for layout, spacing, colors, responsive breakpoints
- [ ] Do NOT override Material component styles with Tailwind
- [ ] Common classes:
  - Layout: `flex`, `grid`, `flex-col`, `flex-row`
  - Spacing: `p-4`, `m-4`, `gap-4`, `space-y-2`
  - Responsive: `md:`, `lg:` breakpoints
  - Colors: `bg-blue-500`, `text-white`, `bg-gray-100`
  - Sizing: `w-full`, `h-full`, `max-w-4xl`

### Message Bubble Styling
- [ ] Sender: `bg-blue-500 text-white rounded-lg p-3 ml-auto max-w-xs`
- [ ] Receiver: `bg-gray-200 text-black rounded-lg p-3 mr-auto max-w-xs`

### Responsive Breakpoints
- [ ] Mobile: < 768px (sm) - full-screen chat, collapsible sidebar
- [ ] Tablet: 768px - 1024px (md) - sidebar visible, narrower chat
- [ ] Desktop: > 1024px (lg) - sidebar + chat side-by-side

---

## Project Structure

```
chat-app/
├── src/
│   ├── app/
│   │   ├── components/              # Dumb/Presentational components
│   │   │   ├── sidebar/
│   │   │   │   ├── sidebar.component.ts        # AC-7.1 to AC-7.12
│   │   │   │   ├── sidebar.component.html
│   │   │   │   └── sidebar.component.scss
│   │   │   ├── message-bubble/                 # AC-10.1 to AC-10.7
│   │   │   ├── message-input/                  # AC-11.1 to AC-11.7
│   │   │   └── new-chat-dialog/                # AC-12.1 to AC-12.7
│   │   ├── pages/                   # Smart/Container components
│   │   │   ├── login/                          # AC-5.1 to AC-5.10
│   │   │   ├── chat-layout/                    # AC-6.1 to AC-6.7
│   │   │   ├── conversations-list/             # AC-8.1 to AC-8.5
│   │   │   └── chat-window/                    # AC-9.1 to AC-9.12
│   │   ├── services/
│   │   │   ├── auth.service.ts                 # AC-1.1 to AC-1.10 (MOCK)
│   │   │   ├── chat.service.ts                 # AC-2.1 to AC-2.12 (localStorage)
│   │   │   └── contacts.service.ts             # AC-3.1 to AC-3.3 (MOCK)
│   │   ├── guards/
│   │   │   └── auth.guard.ts                   # AC-4.5 (check isAuthenticated)
│   │   ├── models/
│   │   │   ├── user.model.ts
│   │   │   ├── conversation.model.ts
│   │   │   └── message.model.ts
│   │   ├── app.component.ts
│   │   ├── app.component.html
│   │   ├── app.config.ts
│   │   └── app.routes.ts                       # AC-4.1 to AC-4.6
│   ├── styles.scss                  # Global styles + Material theme
│   └── index.html
├── angular.json
├── package.json
├── tsconfig.json
└── tailwind.config.js
```

**Component Size Guidelines:**
- Smart components: < 150 lines
- Dumb components: < 80 lines
- Services: < 250 lines (including mock data)
- Each file should have a single responsibility

---

## Quick Start Checklist

### 1. Setup Angular Project
```bash
ng new chat-app --routing --style=scss
cd chat-app
ng add @angular/material
# Choose a theme, setup typography, include animations

# Install Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init
# Configure tailwind.config.js and styles.scss
```

### 2. Create Services First
```bash
ng generate service services/auth
ng generate service services/chat
ng generate service services/contacts
ng generate guard guards/auth
```
- TODO: Implement AC-1.1 to AC-1.10 in AuthService
- TODO: Implement AC-2.1 to AC-2.12 in ChatService
- TODO: Implement AC-3.1 to AC-3.3 in ContactsService
- TODO: Implement AuthGuard (AC-4.5)

### 3. Create Models
```bash
mkdir src/app/models
# Create user.model.ts, conversation.model.ts, message.model.ts
```

### 4. Create Dumb Components (Standalone)
```bash
ng generate component components/sidebar --standalone
ng generate component components/message-bubble --standalone
ng generate component components/message-input --standalone
ng generate component components/new-chat-dialog --standalone
```

### 5. Create Smart Components (Pages)
```bash
ng generate component pages/login
ng generate component pages/chat-layout
ng generate component pages/conversations-list
ng generate component pages/chat-window
```

### 6. Configure Routes
- TODO: Add all routes to app.routes.ts (AC-4.1 to AC-4.6)

### 7. Test Workflow
1. Login with demo@example.com / demo123
2. Click "New Chat" → Select contact
3. Send message → See auto-response after 2 seconds
4. Switch between conversations
5. Test on mobile (< 768px) - sidebar should collapse
6. Logout → Should redirect to /login

---

## Development Notes

**⚠️ CRITICAL: No Backend Integration**
- Do NOT create any HTTP services
- Do NOT use HttpClient anywhere
- Do NOT implement WebSockets
- All data is mocked in services
- All storage is localStorage only
- "Real-time" is simulated with setTimeout

**localStorage Keys:**
- `chat_current_user` - Current logged-in user
- `chat_users` - Demo users database
- `chat_conversations` - All conversations
- `chat_messages` - All messages (or nested in conversations)

**Component Best Practices:**
- Use OnPush change detection for dumb components
- Keep templates simple (< 50 lines)
- Extract complex logic to helper methods
- Use async pipe for observables
- Implement OnDestroy for subscriptions cleanup

**Simulating Real-time:**
```typescript
// After sending message, simulate response
setTimeout(() => {
  this.chatService.simulateIncomingMessage(conversationId);
}, 2000 + Math.random() * 2000); // 2-4 seconds delay
```

**Testing Strategy:**
- Manual testing only for MVP
- Use Chrome DevTools for responsive testing
- Test all AC checkboxes before marking feature complete
- Test with multiple demo users in different browser tabs

---

## Additional Features (Optional, Post-MVP)

### Nice-to-Have Features
- [ ] Typing indicator (show when other user is typing)
- [ ] Read receipts (show if message was read)
- [ ] Message reactions (emoji reactions)
- [ ] Group chats (multiple participants)
- [ ] File attachments (images, documents)
- [ ] Message search
- [ ] User profile editing
- [ ] Theme toggle (light/dark mode)
- [ ] Notification sounds
- [ ] Unread message count badges
- [ ] Message deletion
- [ ] Emoji picker
- [ ] Voice messages
- [ ] Video calls (would require real backend)

---

## Testing Checklist

### Manual Testing
- [ ] Login with demo credentials works
- [ ] Login with wrong credentials shows error
- [ ] Already authenticated redirects to /chat
- [ ] Logout works and redirects to /login
- [ ] Create new conversation works
- [ ] Send message appears immediately
- [ ] Incoming message appears after 2-4 seconds
- [ ] Messages persist after page refresh (localStorage)
- [ ] Switch between conversations works
- [ ] Delete conversation works (with confirmation)
- [ ] Sidebar shows all conversations
- [ ] Last message preview updates
- [ ] Timestamps display correctly
- [ ] Auto-scroll to bottom on new message
- [ ] Mobile: sidebar collapses
- [ ] Mobile: toggle sidebar button works
- [ ] Tablet: sidebar + chat side-by-side
- [ ] Desktop: full layout
- [ ] Browser back/forward navigation works

### Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Acceptance Criteria Summary

**Total: 92 Testable Acceptance Criteria**

- **AC-1.x:** AuthService (10 criteria)
- **AC-2.x:** ChatService (12 criteria)
- **AC-3.x:** ContactsService (3 criteria)
- **AC-4.x:** Routing (6 criteria)
- **AC-5.x:** Login Component (10 criteria)
- **AC-6.x:** Chat Layout (7 criteria)
- **AC-7.x:** Sidebar Component (12 criteria)
- **AC-8.x:** Conversations List (5 criteria)
- **AC-9.x:** Chat Window (12 criteria)
- **AC-10.x:** Message Bubble (7 criteria)
- **AC-11.x:** Message Input (7 criteria)
- **AC-12.x:** New Chat Dialog (7 criteria)

---

**Last Updated:** November 5, 2025  
**Version:** 1.0  
**For:** Angular Material + Tailwind Chat Application (Mock Data + localStorage ONLY)

