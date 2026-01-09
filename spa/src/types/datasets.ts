export interface Dataset {
  id: string;
  name?: string;
  url?: string;
  info_hash?: string;
  size_in_bytes?: number;
  added_date?: string;
  number_of_files?: number;
  number_of_downloads?: number;
  uploaded_by?: string;
  uploaded_by_url?: string;
}
