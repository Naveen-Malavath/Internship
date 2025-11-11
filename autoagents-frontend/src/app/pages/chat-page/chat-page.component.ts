import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

import { App } from '../../app';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [RouterModule, App],
  templateUrl: './chat-page.component.html',
  styleUrls: ['./chat-page.component.scss'],
})
export class ChatPageComponent {}

