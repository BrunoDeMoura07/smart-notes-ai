import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'notes' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login').then((m) => m.Login),
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register/register').then((m) => m.Register),
  },
  {
    path: 'notes',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/notes/note-list/note-list').then((m) => m.NoteList),
  },
  {
    path: 'notes/new',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/notes/note-create/note-create').then((m) => m.NoteCreate),
  },
  {
    path: 'notes/:id',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/notes/note-detail/note-detail').then((m) => m.NoteDetail),
  },
  { path: '**', redirectTo: 'notes' },
];
