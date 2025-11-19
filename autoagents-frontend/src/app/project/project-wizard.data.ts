import { ProjectAISuggestion, ProjectTemplate, ProjectWorkflowPreset } from '../types';

export const PROJECT_WORKFLOWS: ProjectWorkflowPreset[] = [
  {
    id: 'scrum-flow',
    name: 'Scrum Iterations',
    description: 'Two-week sprints with backlog grooming, sprint review, and retro checkpoints.',
    issueTypes: ['Epic', 'Story', 'Task', 'Bug'],
    defaultBoard: 'scrum',
    recommendedSprintLength: 14,
    notes: 'Ideal for teams that commit to sprint ceremonies and velocity tracking.',
  },
  {
    id: 'kanban-flow',
    name: 'Kanban Delivery',
    description: 'Continuous flow board with WIP limits to unblock teams quickly.',
    issueTypes: ['Epic', 'Task', 'Bug'],
    defaultBoard: 'kanban',
    notes: 'Great for ops or platform teams that favour steady flow over time-boxing.',
  },
  {
    id: 'hybrid-flow',
    name: 'Dual-Track Discovery',
    description:
      'Blends discovery and delivery tracks with weekly checkpoints and outcome tracking.',
    issueTypes: ['Epic', 'Story', 'Task', 'Research', 'Experiment'],
    defaultBoard: 'mixed',
    recommendedSprintLength: 7,
    notes: 'Balances discovery spikes with rapid releases for product teams.',
  },
];

export const PROJECT_AI_SUGGESTIONS: ProjectAISuggestion[] = [
  {
    id: 'exec-summary',
    title: 'Project summary',
    category: 'summary',
    prompt:
      'Draft an executive summary for a {industry} initiative focused on {focusAreas}. Highlight customer impact and business outcomes in under 120 words.',
  },
  {
    id: 'epic-seeds',
    title: 'Epic-level roadmap ideas',
    category: 'epics',
    prompt:
      'Provide 4-6 epic level initiatives for a {methodology} team launching a {industry} product. Each epic should include a single sentence justification.',
  },
  {
    id: 'acceptance-criteria',
    title: 'Acceptance criteria checklist',
    category: 'acceptanceCriteria',
    prompt:
      'List key acceptance criteria for the MVP release of a {industry} product that emphasises {focusAreas}. Format as bullet points.',
  },
  {
    id: 'risk-register',
    title: 'Delivery risk register',
    category: 'stories',
    prompt:
      'Summarise the top delivery risks for a {methodology} implementation, covering technology, compliance, and people considerations.',
  },
];

export const PROJECT_TEMPLATES: ProjectTemplate[] = [
  {
    id: 'digital-banking',
    name: 'Digital Banking Suite',
    summary:
      'Deliver a secure, personalised banking experience with account management, payments, and analytics.',
    industry: 'Financial Services',
    methodology: 'scrum',
    defaultWorkflow: 'scrum-flow',
    focusAreas: ['security', 'compliance', 'mobile-first experience'],
    personaHints: ['Compliance Lead', 'Branch Manager', 'Mobile UX Specialist'],
    aiPrompts: PROJECT_AI_SUGGESTIONS,
  },
  {
    id: 'commerce-platform',
    name: 'Composable Commerce',
    summary:
      'Create a modular e-commerce platform with headless storefronts, inventory orchestration, and loyalty.',
    industry: 'Retail & eCommerce',
    methodology: 'hybrid',
    defaultWorkflow: 'hybrid-flow',
    focusAreas: ['performance', 'catalog scalability', 'personalisation'],
    personaHints: ['Merchandising Lead', 'Growth Marketer', 'Fulfilment Analyst'],
    aiPrompts: PROJECT_AI_SUGGESTIONS,
  },
  {
    id: 'support-ai',
    name: 'AI-powered Support Desk',
    summary:
      'Roll out an AI-assisted support desk with conversational automation and proactive insights.',
    industry: 'SaaS / Customer Success',
    methodology: 'kanban',
    defaultWorkflow: 'kanban-flow',
    focusAreas: ['self-service automation', 'agent productivity', 'analytics'],
    personaHints: ['Support Operations', 'CX Lead', 'Knowledge Manager'],
    aiPrompts: PROJECT_AI_SUGGESTIONS,
  },
];

export const PROJECT_TIMEZONES: string[] = [
  'UTC',
  'America/New_York',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Berlin',
  'Asia/Dubai',
  'Asia/Kolkata',
  'Asia/Singapore',
  'Australia/Sydney',
];

export const PROJECT_TEAM_SIZES = [5, 8, 10, 12, 15, 20];

export function generateProjectKey(name: string): string {
  const trimmed = name.trim().toUpperCase();
  if (!trimmed) {
    return '';
  }

  const letters = trimmed
    .replace(/[^A-Z0-9 ]/g, '')
    .split(' ')
    .filter((segment) => segment.length)
    .slice(0, 3)
    .map((segment) => segment[0])
    .join('');

  const fallback = trimmed.replace(/[^A-Z0-9]/g, '').slice(0, 3);
  return (letters || fallback).padEnd(3, 'X');
}

