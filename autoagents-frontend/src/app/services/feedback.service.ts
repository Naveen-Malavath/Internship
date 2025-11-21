import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry, timeout, map } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { FeedbackRequest, FeedbackResponse, FeedbackHistoryEntry } from '../types';

@Injectable({
  providedIn: 'root',
})
export class FeedbackService {
  private readonly apiUrl = environment.apiUrl || 'http://localhost:8000';
  private readonly FEEDBACK_TIMEOUT = 60000; // 60 seconds
  private readonly MAX_RETRIES = 2;

  constructor(private http: HttpClient) {
    console.debug('[FeedbackService] Service initialized', {
      apiUrl: this.apiUrl,
      timeout: this.FEEDBACK_TIMEOUT,
      maxRetries: this.MAX_RETRIES,
    });
  }

  submitFeedback(request: FeedbackRequest): Observable<FeedbackResponse> {
    console.debug('[FeedbackService] Submitting feedback', {
      itemId: request.itemId,
      itemType: request.itemType,
      feedbackLength: request.feedback.length,
    });

    return this.http
      .post<FeedbackResponse>(`${this.apiUrl}/api/feedback/submit`, request)
      .pipe(
        timeout(this.FEEDBACK_TIMEOUT),
        retry(this.MAX_RETRIES),
        catchError(this.handleError.bind(this))
      );
  }

  regenerateContent(request: FeedbackRequest): Observable<FeedbackResponse> {
    console.debug('[FeedbackService] Regenerating content', {
      itemId: request.itemId,
      itemType: request.itemType,
      hasFeedback: !!request.feedback,
    });

    return this.http
      .post<FeedbackResponse>(`${this.apiUrl}/api/feedback/regenerate`, request)
      .pipe(
        timeout(this.FEEDBACK_TIMEOUT),
        retry(this.MAX_RETRIES),
        catchError(this.handleError.bind(this))
      );
  }

  getFeedbackHistory(
    itemId: string,
    itemType: 'feature' | 'story' | 'visualization'
  ): Observable<FeedbackHistoryEntry[]> {
    console.debug('[FeedbackService] Getting feedback history', {
      itemId,
      itemType,
    });

    return this.http
      .get<FeedbackHistoryEntry[]>(
        `${this.apiUrl}/api/feedback/history/${itemId}?itemType=${itemType}`
      )
      .pipe(
        timeout(10000), // 10 seconds for history
        catchError(this.handleError.bind(this))
      );
  }

  getRegenerationCount(
    itemId: string,
    itemType: 'feature' | 'story' | 'visualization'
  ): Observable<number> {
    console.debug('[FeedbackService] Getting regeneration count', {
      itemId,
      itemType,
    });

    return this.http
      .get<{ count: number }>(
        `${this.apiUrl}/api/feedback/regeneration-count/${itemId}?itemType=${itemType}`
      )
      .pipe(
        timeout(10000),
        // Map the response to just the number
        map((response) => response.count),
        catchError((error) => {
          console.warn('[FeedbackService] Error getting regeneration count', error);
          // Return 0 if error (graceful degradation)
          return throwError(() => error);
        })
      );
  }

  private handleError(error: HttpErrorResponse | Error): Observable<never> {
    console.error('[FeedbackService] Error occurred', error);

    let errorMessage = 'An unknown error occurred';
    let errorCode = 'UNKNOWN_ERROR';

    if (error instanceof HttpErrorResponse) {
      console.error('[FeedbackService] HTTP error', {
        status: error.status,
        statusText: error.statusText,
        error: error.error,
      });

      errorCode = error.error?.code || `HTTP_${error.status}`;
      errorMessage =
        error.error?.message ||
        error.error?.detail ||
        `HTTP ${error.status}: ${error.statusText}`;

      // Handle specific error codes
      if (error.status === 429) {
        errorCode = 'RATE_LIMIT_EXCEEDED';
        errorMessage = 'Rate limit exceeded. Please try again later.';
      } else if (error.status === 503) {
        errorCode = 'SERVICE_UNAVAILABLE';
        errorMessage = 'Service temporarily unavailable. Please try again later.';
      } else if (error.status === 504) {
        errorCode = 'TIMEOUT';
        errorMessage = 'Request timed out. Please try again.';
      }
    } else if (error instanceof Error) {
      console.error('[FeedbackService] Error object', {
        name: error.name,
        message: error.message,
        stack: error.stack,
      });

      if (error.name === 'TimeoutError' || error.message?.includes('timeout')) {
        errorCode = 'TIMEOUT';
        errorMessage = 'Request timed out. Please try again.';
      } else {
        errorMessage = error.message;
      }
    }

    return throwError(() => ({
      code: errorCode,
      message: errorMessage,
      error: error,
    }));
  }
}

