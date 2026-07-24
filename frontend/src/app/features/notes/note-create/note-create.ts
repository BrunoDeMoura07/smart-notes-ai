import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';

import { extractErrorMessage } from '../../../core/interceptors/error.interceptor';
import { NotesService } from '../../../core/services/notes.service';

type CreateMode = 'text' | 'file';

@Component({
  selector: 'app-note-create',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatButtonToggleModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './note-create.html',
  styleUrl: './note-create.scss',
})
export class NoteCreate {
  private readonly fb = inject(FormBuilder);
  private readonly notesService = inject(NotesService);
  private readonly router = inject(Router);

  readonly mode = signal<CreateMode>('text');
  readonly loading = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly selectedFile = signal<File | null>(null);

  readonly form = this.fb.nonNullable.group({
    title: [''],
    content: [''],
  });

  setMode(mode: CreateMode): void {
    this.mode.set(mode);
    this.errorMessage.set(null);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
  }

  submit(): void {
    if (this.loading()) {
      return;
    }

    this.errorMessage.set(null);
    const title = this.form.getRawValue().title || undefined;

    if (this.mode() === 'text') {
      const content = this.form.getRawValue().content.trim();
      if (!content) {
        this.errorMessage.set('Cole algum texto antes de enviar.');
        return;
      }
      this.loading.set(true);
      this.notesService.createTextNote(content, title).subscribe({
        next: (result) => this.router.navigate(['/notes', result.id]),
        error: (error) => {
          this.loading.set(false);
          this.errorMessage.set(extractErrorMessage(error));
        },
      });
      return;
    }

    const file = this.selectedFile();
    if (!file) {
      this.errorMessage.set('Selecione um arquivo (PDF ou áudio) antes de enviar.');
      return;
    }
    this.loading.set(true);
    this.notesService.uploadNote(file, title).subscribe({
      next: (result) => this.router.navigate(['/notes', result.id]),
      error: (error) => {
        this.loading.set(false);
        this.errorMessage.set(extractErrorMessage(error));
      },
    });
  }
}
