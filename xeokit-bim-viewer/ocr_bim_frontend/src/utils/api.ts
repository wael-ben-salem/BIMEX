import { DetectedSymbol, ExtractedText, StructuralElement } from "../types";

// ---------- FILES ----------
export async function uploadFileToBackend(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8001/ocr/files/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Upload failed");
  }

  return response.json();
}

export async function listFiles() {
  const response = await fetch("http://localhost:8001/files");

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to list files");
  }

  return response.json();
}

export async function getFileDetails(fileId: string) {
  const response = await fetch(`http://localhost:8001/ocr/files/${fileId}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get file details");
  }

  return response.json();
}

export async function deleteFile(fileId: string) {
  const response = await fetch(`http://localhost:8001/ocr/files/${fileId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to delete file");
  }

  return response.json();
}

export async function getFileThumbnail(fileId: string) {
  const response = await fetch(
    `http://localhost:8001/ocr/files/${fileId}/thumbnail`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get thumbnail");
  }

  return response.blob(); // thumbnail is likely an image
}

// ---------- PROCESSING ----------
export async function startProcessing(
  fileId: string,
  options: {
    enable_ocr: boolean;
    enable_vision: boolean;
    languages: string[];
    use_llm: boolean;
  }
) {
  const response = await fetch(`http://localhost:8001/ocr/process/process/${fileId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(options),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to start processing");
  }

  return response.json();
}

export async function getProcessingStatus(fileId: string) {
  const response = await fetch(
    `http://localhost:8001/ocr/process/process/${fileId}/status`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get processing status");
  }

  return response.json();
}

export async function cancelProcessing(fileId: string) {
  const response = await fetch(
    `http://localhost:8001/ocr/process/process/${fileId}/cancel`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to cancel processing");
  }

  return response.json();
}

export async function getProcessingQueue() {
  const response = await fetch("http://localhost:8001/ocr/process/process/queue");

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get processing queue");
  }

  return response.json();
}

// ---------- RESULTS ----------
export async function getAllResults(fileId: string) {
  const response = await fetch(`http://localhost:8001/ocr/results/${fileId}`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get all results");
  }

  return response.json();
}

export async function getTextResults(fileId: string) {
  const response = await fetch(`http://localhost:8001/ocr/results/${fileId}/text`);

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get text results");
  }

  return response.json();
}

export async function getDimensionsResults(fileId: string) {
  const response = await fetch(
    `http://localhost:8001/ocr/results/${fileId}/dimensions`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get dimensions results");
  }

  return response.json();
}

export async function getSymbolsResults(fileId: string) {
  const response = await fetch(
    `http://localhost:8001/ocr/results/${fileId}/symbols`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get symbols results");
  }

  return response.json();
}

export async function getElementsResults(fileId: string) {
  const response = await fetch(
    `http://localhost:8001/ocr/results/${fileId}/elements`
  );

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to get elements results");
  }

  return response.json();
}


// ---------- EXPORT ----------

// ---------- EXPORT ----------
export async function exportCSV(fileId: string) {
  try {
    const response = await fetch(`http://localhost:8001/ocr/results/${fileId}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to export CSV");
    }

    const data = await response.json();

    // Flatten OCR results
    const ocrResults: {
      category: string;
      text: string;
      type: string;
      x: number;
      y: number;
      width: number;
      height: number;
      confidence: number;
    }[] = (data.ocr?.results || []).map((r: ExtractedText) => ({
      category: 'OCR',
      text: r.text,
      type: r.type,
      x: r.x,
      y: r.y,
      width: r.width,
      height: r.height,
      confidence: r.confidence,
    }));

    // Flatten symbols
    const symbolResults: {
      category: string;
      name: string;
      bbox: string;
      confidence: number;
    }[] = (data.vision?.symbols || []).map((s: DetectedSymbol) => ({
      category: 'Symbol',
      name: s.name,
      bbox: s.bbox.join(','), // symbols still have bbox
      confidence: s.confidence,
    }));

    // Flatten elements (adjusted for x, y, width, height)
    const elementResults: {
      category: string;
      element_type: string;
      x: number;
      y: number;
      width: number;
      height: number;
      confidence: number;
    }[] = (data.vision?.elements || []).map((e: StructuralElement) => ({
      category: 'Element',
      element_type: e.element_type,
      x: e.x,
      y: e.y,
      width: e.width,
      height: e.height,
      confidence: e.confidence,
    }));

    // Combine all rows
    const allRows = [...ocrResults, ...symbolResults, ...elementResults];

    if (allRows.length === 0) {
      alert("No data to export");
      return;
    }

    // Convert to CSV
    const headers = Object.keys(allRows[0]);
    const csvRows = [
      headers.join(","), // header row
      ...allRows.map(row =>
        headers.map(h => `"${String((row as any)[h]).replace(/"/g, '""')}"`).join(",")
      ),
    ];
    const csvString = csvRows.join("\n");

    // Trigger download
    const blob = new Blob([csvString], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "results.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

  } catch (err: any) {
    console.error("Export CSV failed:", err);
    alert(err.message || "Failed to export CSV");
  }
}



export async function exportJSON(fileId: string) {
  const results = await getAllResults(fileId);
  const blob = new Blob([JSON.stringify(results, null, 2)], {
    type: "application/json",
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "results.json");
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
