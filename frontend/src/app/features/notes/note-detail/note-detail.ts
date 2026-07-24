import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { interval, startWith, switchMap, takeWhile } from 'rxjs';

import { extractErrorMessage } from '../../../core/interceptors/error.interceptor';
import { Note } from '../../../core/models/note.model';
import { NotesService } from '../../../core/services/notes.service';
import { StatusBadge } from '../../../shared/components/status-badge/status-badge';

const POLL_INTERVAL_MS = 2000;
const MAX_POLL_DURATION_MS = 3 * 60 * 1000;

@Component({
  selector: 'app-note-detail',
  standalone: true,
  imports: [RouterLink, StatusBadge, MatCardModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './note-detail.html',
  styleUrl: './note-detail.scss',
})
export class NoteDetail {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly notesService = inject(NotesService);
  private readonly destroyRef = inject(DestroyRef);

  private readonly noteId = this.route.snapshot.paramMap.get('id')!;

  readonly note = signal<Note | null>(null);
  readonly loading = signal(true);
  readonly deleting = signal(false);
  readonly pollTimedOut = signal(false);
  readonly loadError = signal<string | null>(null);

  constructor() {
    this.startPolling();
  }

  private startPolling(): void {
    const startedAt = Date.now();

    interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.notesService.getNote(this.noteId)),
        takeWhile((note) => {
          const stillProcessing = note.status === 'pending' || note.status === 'processing';
          if (stillProcessing && Date.now() - startedAt > MAX_POLL_DURATION_MS) {
            this.pollTimedOut.set(true);
            return false;
          }
          return stillProcessing;
        }, true),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe({
        next: (note) => {
          this.note.set(note);
          this.loading.set(false);
          this.loadError.set(null);
        },
        error: (error) => {
          this.loading.set(false);
          this.loadError.set(extractErrorMessage(error, 'Não foi possível carregar a nota.'));
        },
      });
  }

  refresh(): void {
    this.loading.set(true);
    this.pollTimedOut.set(false);
    this.startPolling();
  }

  deleteNote(): void {
    this.deleting.set(true);
    this.notesService.deleteNote(this.noteId).subscribe({
      next: () => this.router.navigate(['/notes']),
      error: () => this.deleting.set(false),
    });
  }
}
