import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { User } from '../models/user.model';
import { TokenStorageService } from './token-storage.service';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

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
  private readonly tokenStorage = inject(TokenStorageService);

  private readonly hasTokenSignal = signal(!!this.tokenStorage.getToken());
  readonly isAuthenticated = computed(() => this.hasTokenSignal());

  register(payload: RegisterPayload): Observable<User> {
    return this.http.post<User>(`${environment.apiUrl}/auth/register`, payload);
  }

  login(payload: LoginPayload): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, payload).pipe(
      tap((response) => {
        this.tokenStorage.setToken(response.access_token);
        this.hasTokenSignal.set(true);
      })
    );
  }

  me(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/auth/me`);
  }

  logout(): void {
    this.tokenStorage.clearToken();
    this.hasTokenSignal.set(false);
  }
}
