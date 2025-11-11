import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { fakeAsync, TestBed, tick } from '@angular/core/testing';
import { App } from './app';

describe('App', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create the app', fakeAsync(() => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    fixture.detectChanges();
    httpMock.expectOne('http://localhost:8000/status/right-now').flush({
      status: 'unused test response',
    });
    tick();

    expect(app).toBeTruthy();
  }));

  it('should render workspace headline', fakeAsync(() => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();

    httpMock.expectOne('http://localhost:8000/status/right-now').flush({
      status: 'Autoagents status from test',
    });
    tick();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('AutoAgents Workspace');
    expect(compiled.querySelector('workspace-view h1')?.textContent).toContain('Mermaid Studio');
  }));

  it('should surface the LangChain status text', fakeAsync(() => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();

    httpMock.expectOne('http://localhost:8000/status/right-now').flush({
      status: 'Autoagents is ready right now!',
    });
    tick();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.status-indicator')?.textContent).toContain(
      'Autoagents is ready right now!'
    );
  }));

  it('should expose workspace controls', fakeAsync(() => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();

    httpMock.expectOne('http://localhost:8000/status/right-now').flush({
      status: 'Status loaded',
    });
    tick();

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const headerButtons = Array.from(compiled.querySelectorAll('header.app-header button')).map(
      (btn) => (btn as HTMLButtonElement).textContent?.trim()
    );
    expect(headerButtons).toContain('New Project');
    expect(headerButtons).toContain('Add Feature');
    expect(headerButtons).toContain('Open Chat');
  }));

  it('should send messages in chat mode', fakeAsync(() => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();

    httpMock.expectOne('http://localhost:8000/status/right-now').flush({
      status: 'Status ready',
    });
    tick();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const openChatButton = Array.from(
      compiled.querySelectorAll('header.app-header button')
    ).find((btn) => (btn as HTMLButtonElement).textContent?.includes('Open Chat')) as HTMLButtonElement;
    expect(openChatButton).toBeTruthy();
    openChatButton.click();
    fixture.detectChanges();

    const textarea = compiled.querySelector('textarea') as HTMLTextAreaElement;
    textarea.value = 'Hello assistant';
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const form = compiled.querySelector('form.chat-input') as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    httpMock.expectOne('http://localhost:8000/agent/features').flush({
      run_id: 'run-1',
      summary: 'Generated feature summary',
      message: 'Generated features',
      decision: 'generated',
      features: [
        {
          title: 'Sample Feature',
          description: 'A generated feature for testing.',
          acceptanceCriteria: ['Given the user is in chat, when they ask for help, then respond.'],
        },
      ],
    });
    tick();
    fixture.detectChanges();

    const bubbleTexts = Array.from(compiled.querySelectorAll('.chat-bubble')).map((el) =>
      (el as HTMLElement).textContent ?? ''
    );
    expect(bubbleTexts.some((text) => text.includes('Hello assistant'))).toBeTrue();
    expect(bubbleTexts.some((text) => text.includes('Generated feature summary'))).toBeTrue();
  }));
});
