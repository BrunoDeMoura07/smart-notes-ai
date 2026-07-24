import { Component, computed, input } from '@angular/core';

import { NoteStatusValue } from '../../../core/models/note.model';

const LABELS: Record<NoteStatusValue, string> = {
  pending: 'Pendente',
  processing: 'Processando',
  completed: 'Concluído',
  failed: 'Falhou',
};

@Component({
  selector: 'app-status-badge',
  standalone: true,
  template: `<span class="badge badge--{{ status() }}">{{ label() }}</span>`,
  styleUrl: './status-badge.scss',
})
export class StatusBadge {
  readonly status = input.required<NoteStatusValue>();
  readonly label = computed(() => LABELS[this.status()]);
}
