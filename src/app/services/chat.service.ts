import { Injectable, signal } from '@angular/core';
import { Message, Conversation } from '../models/message.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private conversationsSignal = signal<Conversation[]>([]);
  private currentConversationSignal = signal<Conversation | null>(null);

  conversations = this.conversationsSignal.asReadonly();
  currentConversation = this.currentConversationSignal.asReadonly();

  constructor() {
    this.loadConversations();
    
    // Create a default conversation if none exist
    if (this.conversationsSignal().length === 0) {
      this.createNewConversation();
    } else {
      this.currentConversationSignal.set(this.conversationsSignal()[0]);
    }
  }

  private loadConversations(): void {
    const saved = localStorage.getItem('conversations');
    if (saved) {
      const conversations = JSON.parse(saved, (key, value) => {
        if (key === 'timestamp' || key === 'createdAt' || key === 'updatedAt') {
          return new Date(value);
        }
        return value;
      });
      this.conversationsSignal.set(conversations);
    }
  }

  private saveConversations(): void {
    localStorage.setItem('conversations', JSON.stringify(this.conversationsSignal()));
  }

  createNewConversation(): Conversation {
    const newConversation: Conversation = {
      id: this.generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.conversationsSignal.update(convs => [newConversation, ...convs]);
    this.currentConversationSignal.set(newConversation);
    this.saveConversations();

    return newConversation;
  }

  selectConversation(conversationId: string): void {
    const conversation = this.conversationsSignal().find(c => c.id === conversationId);
    if (conversation) {
      this.currentConversationSignal.set(conversation);
    }
  }

  async sendMessage(content: string): Promise<void> {
    const current = this.currentConversationSignal();
    if (!current) return;

    // Add user message
    const userMessage: Message = {
      id: this.generateId(),
      content,
      role: 'user',
      timestamp: new Date()
    };

    this.addMessageToConversation(current.id, userMessage);

    // Update conversation title if it's the first message
    if (current.messages.length === 1) {
      this.updateConversationTitle(current.id, content.slice(0, 50) + (content.length > 50 ? '...' : ''));
    }

    // Add loading message
    const loadingMessage: Message = {
      id: this.generateId(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isLoading: true
    };

    this.addMessageToConversation(current.id, loadingMessage);

    // Simulate AI response
    setTimeout(() => {
      const response = this.generateResponse(content);
      this.updateMessage(current.id, loadingMessage.id, response);
    }, 1500);
  }

  private addMessageToConversation(conversationId: string, message: Message): void {
    this.conversationsSignal.update(convs => 
      convs.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            messages: [...conv.messages, message],
            updatedAt: new Date()
          };
        }
        return conv;
      })
    );

    // Update current conversation
    const updated = this.conversationsSignal().find(c => c.id === conversationId);
    if (updated) {
      this.currentConversationSignal.set(updated);
    }

    this.saveConversations();
  }

  private updateMessage(conversationId: string, messageId: string, content: string): void {
    this.conversationsSignal.update(convs =>
      convs.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            messages: conv.messages.map(msg =>
              msg.id === messageId
                ? { ...msg, content, isLoading: false }
                : msg
            ),
            updatedAt: new Date()
          };
        }
        return conv;
      })
    );

    const updated = this.conversationsSignal().find(c => c.id === conversationId);
    if (updated) {
      this.currentConversationSignal.set(updated);
    }

    this.saveConversations();
  }

  private updateConversationTitle(conversationId: string, title: string): void {
    this.conversationsSignal.update(convs =>
      convs.map(conv =>
        conv.id === conversationId ? { ...conv, title } : conv
      )
    );

    const updated = this.conversationsSignal().find(c => c.id === conversationId);
    if (updated) {
      this.currentConversationSignal.set(updated);
    }

    this.saveConversations();
  }

  deleteConversation(conversationId: string): void {
    this.conversationsSignal.update(convs => convs.filter(c => c.id !== conversationId));
    
    if (this.currentConversationSignal()?.id === conversationId) {
      const remaining = this.conversationsSignal();
      if (remaining.length > 0) {
        this.currentConversationSignal.set(remaining[0]);
      } else {
        this.createNewConversation();
      }
    }

    this.saveConversations();
  }

  clearAllConversations(): void {
    this.conversationsSignal.set([]);
    this.createNewConversation();
    this.saveConversations();
  }

  private generateResponse(userMessage: string): string {
    // Simple AI response simulation - in production, this would call an API
    const responses = [
      `I understand you're asking about "${userMessage.slice(0, 30)}...". This is a simulated response. In a production environment, this would be connected to an actual AI API like OpenAI's GPT or similar services.`,
      
      `That's an interesting question! To properly answer your query about "${userMessage.slice(0, 30)}...", I would need to be connected to a real AI backend. Currently, this is a demonstration of the chat interface.`,
      
      `I've received your message: "${userMessage.slice(0, 50)}...". In a live system, I would process this through an AI model and provide you with a helpful, contextual response.`,
      
      `Thank you for your question. This chatbot interface is fully functional and ready to be connected to any AI API (OpenAI, Anthropic, Google AI, etc.). Your message "${userMessage.slice(0, 30)}..." would be processed by the AI service.`
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}



