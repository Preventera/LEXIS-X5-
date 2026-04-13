const API_BASE = "http://localhost:8000/api/v1";

export interface UploadResponse {
  filename: string;
  pages: number;
  tables_count: number;
  elements_count: number;
  markdown: string;
  json_data: Record<string, unknown>;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Erreur inconnue" }));
    throw new ApiError(response.status, body.detail ?? "Erreur inconnue");
  }

  return response.json();
}
