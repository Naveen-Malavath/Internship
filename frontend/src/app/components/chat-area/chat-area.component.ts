import { Component, ElementRef, ViewChild, effect, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ChatService } from '../../services/chat.service';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { MessageBubbleComponent } from '../message-bubble/message-bubble.component';

@Component({
  selector: 'app-chat-area',
  standalone: true,
  imports: [CommonModule, FormsModule, SidebarComponent, MessageBubbleComponent],
  templateUrl: './chat-area.component.html',
  styleUrls: ['./chat-area.component.css']
})
export class ChatAreaComponent {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;
  @ViewChild('messageInput') messageInput!: ElementRef;

  currentConversation = this.chatService.currentConversation;
  messageText = signal('');
  isSending = signal(false);

  constructor(private chatService: ChatService) {
    effect(() => {
      const conversation = this.currentConversation();
      if (conversation) {
        setTimeout(() => this.scrollToBottom(), 100);
      }
    });
  }

  async sendMessage(): Promise<void> {
    const text = this.messageText().trim();
    if (!text || this.isSending()) {
      return;
    }

    this.isSending.set(true);
    this.messageText.set('');

    try {
      await this.chatService.sendMessage(text);
    } catch (error) {
      console.error('Failed to send message', error);
    } finally {
      this.isSending.set(false);
      if (this.messageInput) {
        this.messageInput.nativeElement.focus();
      }
    }
  }

  async handleFeedback(event: { conversationId: string; messageId: string; feedback: 'up' | 'down' }): Promise<void> {
    console.debug('[Agent1] Feedback click', event);
    await this.chatService.sendFeedback(event.conversationId, event.messageId, event.feedback);
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  private scrollToBottom(): void {
    if (this.messagesContainer) {
      const element = this.messagesContainer.nativeElement;
      element.scrollTop = element.scrollHeight;
    }
  }
}
