import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Message } from '../../models/message.model';

@Component({
  selector: 'app-message-bubble',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './message-bubble.component.html',
  styleUrls: ['./message-bubble.component.css']
})
export class MessageBubbleComponent {
  @Input({ required: true }) message!: Message;
  @Input({ required: true }) conversationId!: string;

  @Output() feedback = new EventEmitter<{ conversationId: string; messageId: string; feedback: 'up' | 'down' }>();

  onFeedback(feedback: 'up' | 'down'): void {
    if (this.message.isLoading || this.message.feedback === feedback) {
      return;
    }
    this.feedback.emit({
      conversationId: this.conversationId,
      messageId: this.message.id,
      feedback
    });
  }
}
