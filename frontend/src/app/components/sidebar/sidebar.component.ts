import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ChatService } from '../../services/chat.service';
import { AuthService } from '../../services/auth.service';
import { Conversation } from '../../models/message.model';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent {
  conversations = this.chatService.conversations;
  currentConversation = this.chatService.currentConversation;
  currentUser = this.authService.currentUser;

  isCollapsed = false;

  constructor(
    private chatService: ChatService,
    private authService: AuthService
  ) {}

  async newChat(): Promise<void> {
    await this.chatService.createNewConversation();
  }

  selectConversation(conversation: Conversation): void {
    this.chatService.selectConversation(conversation.id);
  }

  async deleteConversation(event: Event, conversationId: string): Promise<void> {
    event.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      await this.chatService.deleteConversation(conversationId);
    }
  }

  async clearAllChats(): Promise<void> {
    if (confirm('Are you sure you want to delete all conversations? This action cannot be undone.')) {
      await this.chatService.clearAllConversations();
    }
  }

  logout(): void {
    if (confirm('Are you sure you want to log out?')) {
      this.authService.logout();
    }
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
  }
}
