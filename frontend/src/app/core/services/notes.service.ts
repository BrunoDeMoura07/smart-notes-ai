import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Note, NoteAccepted, NoteList, NoteStatus } from '../models/note.model';

export interface ListNotesParams {
  search?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}

@Injectable({ providedIn: 'root' })
export class NotesService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/notes`;

  createTextNote(content: string, title?: string): Observable<NoteAccepted> {
    return this.http.post<NoteAccepted>(this.baseUrl, { content, title: title || null });
  }

  uploadNote(file: File, title?: string): Observable<NoteAccepted> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) {
      formData.append('title', title);
    }
    return this.http.post<NoteAccepted>(`${this.baseUrl}/upload`, formData);
  }

  listNotes(params: ListNotesParams = {}): Observable<NoteList> {
    let httpParams = new HttpParams()
      .set('page', String(params.page ?? 1))
      .set('page_size', String(params.pageSize ?? 20));

    if (params.search) {
      httpParams = httpParams.set('search', params.search);
    }
    if (params.status) {
      httpParams = httpParams.set('status', params.status);
    }

    return this.http.get<NoteList>(this.baseUrl, { params: httpParams });
  }

  getNote(id: string): Observable<Note> {
    return this.http.get<Note>(`${this.baseUrl}/${id}`);
  }

  getNoteStatus(id: string): Observable<NoteStatus> {
    return this.http.get<NoteStatus>(`${this.baseUrl}/${id}/status`);
  }

  deleteNote(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
