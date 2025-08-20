export interface DrawingFile {
  id: string;
  backendId:undefined;
  name: string;
  type: string;
  size: number;
  dimensions?: {
    width: number;
    height: number;
  };
  drawingType: DrawingType;
  uploadProgress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  thumbnail?: string;
  url?: string;
}

export type DrawingType = 
  | 'architectural'
  | 'structural' 
  | 'civil'
  | 'infrastructure'
  | 'mep'
  | 'general';

export interface ExtractedText {
  content: any;
  id: string;
  text: string;
  confidence: number; // 0-100 scale
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  type?: 'dimension' | 'label' | 'annotation' | 'title';
}

export interface DetectedSymbol {
  id?: string | number;       // optional, in case API doesn't return an ID
  name: string;               // symbol type returned by API
  bbox: [number, number, number, number]; // [x1, y1, x2, y2]
  confidence: number;
}

export interface StructuralElement {
  id: string;
  type: string;
  confidence: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface AreaCalculation {
  value: any;
  id: string;
  label: string;
  area: number;
  perimeter: number;
  unit: string;
  type: 'room' | 'zone' | 'section' | 'lot' | 'right-of-way';
  coordinates: Array<{x: number; y: number}>;
}

export interface OCRAnalysisResult {
  projectId: string;
  drawingFile: string;
  drawingType: DrawingType;
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  extractedText: ExtractedText[];
  detectedSymbols: DetectedSymbol[];
  structuralElements: StructuralElement[];
  areaCalculations: AreaCalculation[];
  confidenceScores: {
    overall: number;
    text: number;
    symbols: number;
    elements: number;
  };
  processingTime?: number;
  errors?: string[];
}

export interface BIMElement {
  id: string;
  type: string;
  geometry: {
    position: {x: number; y: number; z: number};
    rotation: {x: number; y: number; z: number};
    scale: {x: number; y: number; z: number};
  };
  properties: Record<string, any>;
  layer: string;
  visible: boolean;
}