import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AgentFeatureDetail, AgentFeatureRisk, FeatureFormSubmission } from '../types';

@Component({
  selector: 'feature-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './feature-form.component.html',
  styleUrl: './feature-form.component.scss',
})
export class FeatureFormComponent {
  @Input() open = false;
  @Input() saving = false;
  @Input() set preset(value: AgentFeatureDetail | null) {
    if (!value) {
      return;
    }
    this.detail = this.cloneDetail(value);
  }

  @Output() cancel = new EventEmitter<void>();
  @Output() submit = new EventEmitter<FeatureFormSubmission>();

  protected detail: AgentFeatureDetail = this.createEmptyDetail();
  protected readonly priorityOptions: AgentFeatureDetail['priority'][] = [
    'low',
    'medium',
    'high',
    'critical',
  ];
  protected selectedFiles: File[] = [];

  protected onSummaryBlur(): void {
    if (!this.detail.key.trim() && this.detail.summary.trim()) {
      this.detail.key = this.generateKey(this.detail.summary);
    }
  }

  protected addAcceptanceCriterion(): void {
    this.detail.acceptanceCriteria = [...this.detail.acceptanceCriteria, ''];
  }

  protected updateAcceptanceCriterion(index: number, value: string): void {
    this.detail.acceptanceCriteria = this.detail.acceptanceCriteria.map((criterion, idx) =>
      idx === index ? value : criterion,
    );
  }

  protected removeAcceptanceCriterion(index: number): void {
    this.detail.acceptanceCriteria = this.detail.acceptanceCriteria.filter((_, idx) => idx !== index);
  }

  protected addSuccessMetric(): void {
    this.detail.successMetrics = [...this.detail.successMetrics, ''];
  }

  protected updateSuccessMetric(index: number, value: string): void {
    this.detail.successMetrics = this.detail.successMetrics.map((metric, idx) =>
      idx === index ? value : metric,
    );
  }

  protected removeSuccessMetric(index: number): void {
    this.detail.successMetrics = this.detail.successMetrics.filter((_, idx) => idx !== index);
  }

  protected addStakeholder(): void {
    this.detail.stakeholders = [...this.detail.stakeholders, ''];
  }

  protected updateStakeholder(index: number, value: string): void {
    this.detail.stakeholders = this.detail.stakeholders.map((stakeholder, idx) =>
      idx === index ? value : stakeholder,
    );
  }

  protected removeStakeholder(index: number): void {
    this.detail.stakeholders = this.detail.stakeholders.filter((_, idx) => idx !== index);
  }

  protected addDependency(): void {
    this.detail.dependencies = [...this.detail.dependencies, ''];
  }

  protected updateDependency(index: number, value: string): void {
    this.detail.dependencies = this.detail.dependencies.map((dependency, idx) =>
      idx === index ? value : dependency,
    );
  }

  protected removeDependency(index: number): void {
    this.detail.dependencies = this.detail.dependencies.filter((_, idx) => idx !== index);
  }

  protected addConstraint(): void {
    this.detail.constraints = [...this.detail.constraints, ''];
  }

  protected updateConstraint(index: number, value: string): void {
    this.detail.constraints = this.detail.constraints.map((constraint, idx) =>
      idx === index ? value : constraint,
    );
  }

  protected removeConstraint(index: number): void {
    this.detail.constraints = this.detail.constraints.filter((_, idx) => idx !== index);
  }

  protected addNonFunctionalRequirement(): void {
    this.detail.nonFunctionalRequirements = [...this.detail.nonFunctionalRequirements, ''];
  }

  protected updateNonFunctionalRequirement(index: number, value: string): void {
    this.detail.nonFunctionalRequirements = this.detail.nonFunctionalRequirements.map(
      (requirement, idx) => (idx === index ? value : requirement),
    );
  }

  protected removeNonFunctionalRequirement(index: number): void {
    this.detail.nonFunctionalRequirements = this.detail.nonFunctionalRequirements.filter(
      (_, idx) => idx !== index,
    );
  }

  protected addRisk(): void {
    this.detail.risks = [...this.detail.risks, { description: '', mitigation: '' }];
  }

  protected updateRisk(index: number, value: Partial<AgentFeatureRisk>): void {
    this.detail.risks = this.detail.risks.map((risk, idx) =>
      idx === index ? { ...risk, ...value } : risk,
    );
  }

  protected removeRisk(index: number): void {
    this.detail.risks = this.detail.risks.filter((_, idx) => idx !== index);
  }

  protected onFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) {
      return;
    }

    const files = Array.from(input.files);
    this.selectedFiles = [...this.selectedFiles, ...files];
    input.value = '';
  }

  protected removeFile(index: number): void {
    this.selectedFiles = this.selectedFiles.filter((_, idx) => idx !== index);
  }

  protected onCancel(): void {
    this.cancel.emit();
    this.detail = this.createEmptyDetail();
    this.selectedFiles = [];
  }

  protected onSubmit(): void {
    if (!this.isValid()) {
      return;
    }
    const normalized = this.normalizeDetail(this.detail);
    this.submit.emit({
      detail: normalized,
      files: this.selectedFiles,
    });
    this.detail = this.createEmptyDetail();
    this.selectedFiles = [];
  }

  protected isValid(): boolean {
    return (
      this.detail.summary.trim().length >= 3 &&
      this.detail.problemStatement.trim().length >= 10 &&
      this.detail.businessObjective.trim().length >= 5 &&
      this.detail.userPersona.trim().length >= 3 &&
      this.detail.description.trim().length >= 20 &&
      this.detail.acceptanceCriteria.some((criterion) => criterion.trim().length > 0) &&
      this.detail.successMetrics.some((metric) => metric.trim().length > 0) &&
      this.detail.stakeholders.some((stakeholder) => stakeholder.trim().length > 0) &&
      this.detail.targetRelease.trim().length > 0
    );
  }

  private normalizeDetail(detail: AgentFeatureDetail): AgentFeatureDetail {
    const trimArray = (values: string[]) =>
      values
        .map((value) => value.trim())
        .filter((value, index, arr) => value.length && arr.indexOf(value) === index);

    return {
      summary: detail.summary.trim(),
      key: detail.key.trim() || this.generateKey(detail.summary),
      problemStatement: detail.problemStatement.trim(),
      businessObjective: detail.businessObjective.trim(),
      userPersona: detail.userPersona.trim(),
      description: detail.description.trim(),
      acceptanceCriteria: trimArray(detail.acceptanceCriteria),
      successMetrics: trimArray(detail.successMetrics),
      stakeholders: trimArray(detail.stakeholders),
      dependencies: trimArray(detail.dependencies),
      constraints: trimArray(detail.constraints),
      risks: detail.risks
        .map((risk) => ({
          description: risk.description.trim(),
          mitigation: risk.mitigation.trim(),
        }))
        .filter((risk) => risk.description.length || risk.mitigation.length),
      targetRelease: detail.targetRelease.trim(),
      priority: detail.priority,
      nonFunctionalRequirements: trimArray(detail.nonFunctionalRequirements),
      status: detail.status.trim() || 'Draft',
      team: detail.team.trim(),
    };
  }

  private createEmptyDetail(): AgentFeatureDetail {
    return {
      summary: '',
      key: '',
      problemStatement: '',
      businessObjective: '',
      userPersona: '',
      description: '',
      acceptanceCriteria: [''],
      successMetrics: [''],
      stakeholders: [''],
      dependencies: [],
      constraints: [],
      risks: [],
      targetRelease: '',
      priority: 'medium',
      nonFunctionalRequirements: [],
      status: 'Draft',
      team: '',
    };
  }

  private generateKey(summary: string): string {
    const sanitized = summary.trim().toUpperCase();
    if (!sanitized) {
      return '';
    }
    const segments = sanitized.replace(/[^A-Z0-9 ]/g, '').split(' ').filter(Boolean);
    if (!segments.length) {
      return sanitized.replace(/[^A-Z0-9]/g, '').slice(0, 4) || 'FEAT';
    }
    return segments
      .slice(0, 3)
      .map((segment) => segment.slice(0, 2))
      .join('')
      .slice(0, 6);
  }

  private cloneDetail(detail: AgentFeatureDetail): AgentFeatureDetail {
    return {
      summary: detail.summary,
      key: detail.key,
      problemStatement: detail.problemStatement,
      businessObjective: detail.businessObjective,
      userPersona: detail.userPersona,
      description: detail.description,
      acceptanceCriteria: [...detail.acceptanceCriteria],
      successMetrics: [...detail.successMetrics],
      stakeholders: [...detail.stakeholders],
      dependencies: [...detail.dependencies],
      constraints: [...detail.constraints],
      risks: detail.risks.map((risk) => ({ ...risk })),
      targetRelease: detail.targetRelease,
      priority: detail.priority,
      nonFunctionalRequirements: [...detail.nonFunctionalRequirements],
      status: detail.status,
      team: detail.team,
    };
  }
}

