export interface Warning {
  table?: number;
  row?: number;
  field?: string;
  message: string;
  [key: string]: any;
}

export interface ProcessingResult {
  header_json: any;
  table_csvs: string[];
  full_text_json: any;
  table_crop_image: string;
  original_image: string;
  warnings: Warning[];
  // ✅ Add these new optional fields
  report_pdf?: string;
  llm_review_txt?: string;

  tables?: { index: number; image?: string | null; bbox?: [number, number, number, number]; shape?: [number, number] }[];

}

export interface ProcessedFile {
  id?: string;
  name: string;
  results?: ProcessingResult;
  originalFile?: File;
  status?: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  uploadedAt?: Date;
}

export interface FileUploadProps {
  onFileProcessed: (file: ProcessedFile) => void;
  translateHeaders: boolean;
  enableValidation: boolean;
}

export interface ProcessingResultsProps {
  files: ProcessedFile[];
}
