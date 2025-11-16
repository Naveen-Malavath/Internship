import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AgentStorySpec } from '../types';

@Component({
  selector: 'story-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './story-form.component.html',
  styleUrl: './story-form.component.scss',
})
export class StoryFormComponent {
  @Input() open = false;
  @Input() saving = false;
  @Input() featureTitleReadonly = false;
  @Input() set preset(value: AgentStorySpec | null) {
    if (!value) {
      return;
    }
    this.story = this.cloneStory(value);
  }

  @Output() cancel = new EventEmitter<void>();
  @Output() submit = new EventEmitter<AgentStorySpec>();

  protected story: AgentStorySpec = this.createEmptyStory();

  protected onAddAcceptanceCriterion(): void {
    this.story.acceptanceCriteria = [...this.story.acceptanceCriteria, ''];
  }

  protected onUpdateAcceptanceCriterion(index: number, value: string): void {
    this.story.acceptanceCriteria = this.story.acceptanceCriteria.map((criterion, idx) =>
      idx === index ? value : criterion,
    );
  }

  protected onRemoveAcceptanceCriterion(index: number): void {
    this.story.acceptanceCriteria = this.story.acceptanceCriteria.filter((_, idx) => idx !== index);
  }

  protected onAddImplementationNote(): void {
    this.story.implementationNotes = [...this.story.implementationNotes, ''];
  }

  protected onUpdateImplementationNote(index: number, value: string): void {
    this.story.implementationNotes = this.story.implementationNotes.map((note, idx) =>
      idx === index ? value : note,
    );
  }

  protected onRemoveImplementationNote(index: number): void {
    this.story.implementationNotes = this.story.implementationNotes.filter((_, idx) => idx !== index);
  }

  protected onCancel(): void {
    this.cancel.emit();
    this.resetForm();
  }

  protected onSubmit(): void {
    if (!this.isValid()) {
      return;
    }
    const normalized = this.normalizeStory(this.story);
    this.submit.emit(normalized);
    this.resetForm();
  }

  private resetForm(): void {
    this.story = this.createEmptyStory();
  }

  private isValid(): boolean {
    return (
      this.story.featureTitle.trim().length >= 3 &&
      this.story.userStory.trim().length >= 10 &&
      this.story.acceptanceCriteria.some((criterion) => criterion.trim().length > 0)
    );
  }

  private normalizeStory(story: AgentStorySpec): AgentStorySpec {
    const trimArray = (values: string[]) =>
      values
        .map((value) => value.trim())
        .filter((value, index, arr) => value.length && arr.indexOf(value) === index);

    return {
      featureTitle: story.featureTitle.trim(),
      userStory: story.userStory.trim(),
      acceptanceCriteria: trimArray(story.acceptanceCriteria),
      implementationNotes: trimArray(story.implementationNotes),
    };
  }

  private createEmptyStory(): AgentStorySpec {
    return {
      featureTitle: '',
      userStory: '',
      acceptanceCriteria: [''],
      implementationNotes: [],
    };
  }

  private cloneStory(story: AgentStorySpec): AgentStorySpec {
    return {
      featureTitle: story.featureTitle,
      userStory: story.userStory,
      acceptanceCriteria: [...story.acceptanceCriteria],
      implementationNotes: [...story.implementationNotes],
    };
  }

}


