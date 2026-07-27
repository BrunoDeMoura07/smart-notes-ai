import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, catchError, finalize, map, of, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { User } from '../models/user.model';

interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

interface LoginPayload {
  email: string;
  password: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  private readonly currentUserSignal = signal<User | null>(null);
  readonly isAuthenticated = computed(() => this.currentUserSignal() !== null);

  register(payload: RegisterPayload): Observable<User> {
    return this.http.post<User>(`${environment.apiUrl}/auth/register`, payload);
  }

  login(payload: LoginPayload): Observable<User> {
    return this.http
      .post<User>(`${environment.apiUrl}/auth/login`, payload)
      .pipe(tap((user) => this.currentUserSignal.set(user)));
  }

  me(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/auth/me`).pipe(tap((user) => this.currentUserSignal.set(user)));
  }

  checkSession(): Observable<boolean> {
    return this.me().pipe(
      map(() => true),
      catchError(() => {
        this.currentUserSignal.set(null);
        return of(false);
      })
    );
  }

  logout(): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/auth/logout`, {}).pipe(
      catchError(() => of(void 0)),
      finalize(() => this.currentUserSignal.set(null))
    );
  }
}
