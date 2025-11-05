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

  constructor(private chatService: ChatService) {
    // Auto-scroll when messages change
    effect(() => {
      const conversation = this.currentConversation();
      if (conversation) {
        setTimeout(() => this.scrollToBottom(), 100);
      }
    });
  }

  sendMessage(): void {
    const text = this.messageText().trim();
    if (!text) return;

    this.chatService.sendMessage(text);
    this.messageText.set('');
    this.messageInput.nativeElement.focus();
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

