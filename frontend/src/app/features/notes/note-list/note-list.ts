import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { RouterLink } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';

import { NoteListItem, NoteSourceType } from '../../../core/models/note.model';
import { NotesService } from '../../../core/services/notes.service';
import { StatusBadge } from '../../../shared/components/status-badge/status-badge';

const SOURCE_TYPE_LABELS: Record<NoteSourceType, string> = {
  text: 'Texto',
  pdf: 'PDF',
  audio: 'Áudio',
};

@Component({
  selector: 'app-note-list',
  standalone: true,
  imports: [
    DatePipe,
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    StatusBadge,
  ],
  templateUrl: './note-list.html',
  styleUrl: './note-list.scss',
})
export class NoteList {
  private readonly notesService = inject(NotesService);

  readonly notes = signal<NoteListItem[]>([]);
  readonly total = signal(0);
  readonly loading = signal(true);
  readonly deletingId = signal<string | null>(null);

  readonly searchControl = new FormControl('', { nonNullable: true });
  readonly statusControl = new FormControl<string>('', { nonNullable: true });

  constructor() {
    this.load();

    this.searchControl.valueChanges
      .pipe(debounceTime(300), distinctUntilChanged())
      .subscribe(() => this.load());

    this.statusControl.valueChanges.subscribe(() => this.load());
  }

  load(): void {
    this.loading.set(true);
    this.notesService
      .listNotes({
        search: this.searchControl.value || undefined,
        status: this.statusControl.value || undefined,
      })
      .subscribe({
        next: (result) => {
          this.notes.set(result.items);
          this.total.set(result.total);
          this.loading.set(false);
        },
        error: () => this.loading.set(false),
      });
  }

  sourceTypeLabel(sourceType: NoteSourceType): string {
    return SOURCE_TYPE_LABELS[sourceType];
  }

  deleteNote(id: string): void {
    this.deletingId.set(id);
    this.notesService.deleteNote(id).subscribe({
      next: () => {
        this.deletingId.set(null);
        this.load();
      },
      error: () => this.deletingId.set(null),
    });
  }
}
