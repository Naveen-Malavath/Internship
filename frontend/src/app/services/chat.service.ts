import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { API_BASE_URL } from '../config/api.config';
import { Conversation, Message } from '../models/message.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private conversationsSignal = signal<Conversation[]>([]);
  private currentConversationSignal = signal<Conversation | null>(null);

  conversations = this.conversationsSignal.asReadonly();
  currentConversation = this.currentConversationSignal.asReadonly();

  constructor(private http: HttpClient) {
    this.refreshConversations().catch(error => {
      console.error('Failed to load conversations', error);
    });
  }

  async refreshConversations(selectConversationId?: string): Promise<void> {
    const conversations = await firstValueFrom(
      this.http.get<Conversation[]>(`${API_BASE_URL}/conversations`)
    );

    this.conversationsSignal.set(conversations);

    if (conversations.length === 0) {
      this.currentConversationSignal.set(null);
      return;
    }

    const targetId = selectConversationId ?? this.currentConversationSignal()?.id ?? conversations[0].id;
    const target = conversations.find(conv => conv.id === targetId) ?? conversations[0];
    this.currentConversationSignal.set(target);
  }

  async createNewConversation(title?: string): Promise<void> {
    try {
      const conversation = await firstValueFrom(
        this.http.post<Conversation>(`${API_BASE_URL}/conversations`, title ? { title } : {})
      );
      await this.refreshConversations(conversation.id);
    } catch (error) {
      console.error('Failed to create conversation', error);
    }
  }

  selectConversation(conversationId: string): void {
    const conversation = this.conversationsSignal().find(conv => conv.id === conversationId);
    if (conversation) {
      this.currentConversationSignal.set(conversation);
    }
  }

  async sendMessage(content: string): Promise<void> {
    const current = this.currentConversationSignal();
    if (!current) {
      return;
    }

    const userMessage: Message = {
      id: `temp-user-${Date.now()}`,
      content,
      role: 'user',
      timestamp: new Date().toISOString()
    };
    this.addTemporaryMessage(current.id, userMessage);

    const loadingMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      content: '',
      role: 'assistant',
      timestamp: new Date().toISOString(),
      isLoading: true
    };
    this.addTemporaryMessage(current.id, loadingMessage);

    try {
      const updatedConversation = await firstValueFrom(
        this.http.post<Conversation>(
          `${API_BASE_URL}/conversations/${current.id}/messages`,
          { content }
        )
      );
      this.replaceConversation(updatedConversation);
    } catch (error) {
      console.error('Failed to send message', error);
      this.removeTemporaryMessage(current.id, loadingMessage.id);
      this.removeTemporaryMessage(current.id, userMessage.id);
    }
  }

  async deleteConversation(conversationId: string): Promise<void> {
    try {
      await firstValueFrom(this.http.delete<void>(`${API_BASE_URL}/conversations/${conversationId}`));
      const remainingConversations = this.conversationsSignal().filter(conv => conv.id !== conversationId);
      this.conversationsSignal.set(remainingConversations);

      if (this.currentConversationSignal()?.id === conversationId) {
        await this.refreshConversations();
      }
    } catch (error) {
      console.error('Failed to delete conversation', error);
    }
  }

  async clearAllConversations(): Promise<void> {
    try {
      const conversation = await firstValueFrom(
        this.http.delete<Conversation>(`${API_BASE_URL}/conversations`)
      );
      await this.refreshConversations(conversation.id);
    } catch (error) {
      console.error('Failed to clear conversations', error);
    }
  }

  private addTemporaryMessage(conversationId: string, message: Message): void {
    this.conversationsSignal.update(conversations =>
      conversations.map(conv =>
        conv.id === conversationId
          ? { ...conv, messages: [...conv.messages, message] }
          : conv
      )
    );

    const updated = this.conversationsSignal().find(conv => conv.id === conversationId);
    if (updated) {
      this.currentConversationSignal.set(updated);
    }
  }

  private removeTemporaryMessage(conversationId: string, messageId: string): void {
    this.conversationsSignal.update(conversations =>
      conversations.map(conv =>
        conv.id === conversationId
          ? { ...conv, messages: conv.messages.filter(msg => msg.id !== messageId) }
          : conv
      )
    );

    const updated = this.conversationsSignal().find(conv => conv.id === conversationId);
    if (updated) {
      this.currentConversationSignal.set(updated);
    }
  }

  private replaceConversation(conversation: Conversation): void {
    this.conversationsSignal.update(conversations => {
      const filtered = conversations.filter(conv => conv.id !== conversation.id);
      return [conversation, ...filtered];
    });

    this.currentConversationSignal.set(conversation);
  }
}
