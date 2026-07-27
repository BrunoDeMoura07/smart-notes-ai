import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: unknown) => {
      // /auth/me is used as a "am I logged in?" probe (app bootstrap, route guard) — a 401
      // there just means "not logged in yet", not a session that needs to redirect mid-use.
      const isSessionProbe = req.url.includes('/auth/me');
      if (error instanceof HttpErrorResponse && error.status === 401 && !isSessionProbe) {
        if (!router.url.startsWith('/login')) {
          router.navigate(['/login']);
        }
      }
      return throwError(() => error);
    })
  );
};

export function extractErrorMessage(error: unknown, fallback = 'Algo deu errado. Tente novamente.'): string {
  if (error instanceof HttpErrorResponse) {
    const detail = error.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (error.status === 0) {
      return 'Não foi possível conectar ao servidor.';
    }
  }
  return fallback;
}
