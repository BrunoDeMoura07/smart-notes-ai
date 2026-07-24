export type NoteStatusValue = 'pending' | 'processing' | 'completed' | 'failed';
export type NoteSourceType = 'text' | 'pdf' | 'audio';

export interface NoteAccepted {
  id: string;
  status: NoteStatusValue;
}

export interface NoteStatus {
  id: string;
  status: NoteStatusValue;
  error_message: string | null;
}

export interface Note {
  id: string;
  title: string | null;
  source_type: NoteSourceType;
  original_text: string | null;
  original_filename: string | null;
  summary: string | null;
  tags: string[] | null;
  status: NoteStatusValue;
  error_message: string | null;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface NoteListItem {
  id: string;
  title: string | null;
  source_type: NoteSourceType;
  status: NoteStatusValue;
  created_at: string;
}

export interface NoteList {
  items: NoteListItem[];
  total: number;
  page: number;
  page_size: number;
}
