import { useState, useCallback, useRef } from "react";
import { Upload, FileText, Loader2, AlertCircle, Table, Layers, BookOpen } from "lucide-react";
import { uploadPdf, type UploadResponse, ApiError } from "./services/api";

type Tab = "markdown" | "json";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("markdown");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setError(null);
    setResult(null);
    if (f.type !== "application/pdf") {
      setError("Seuls les fichiers PDF sont acceptés.");
      return;
    }
    if (f.size > 50 * 1024 * 1024) {
      setError("Le fichier dépasse la taille maximale de 50 MB.");
      return;
    }
    setFile(f);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile],
  );

  const onSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadPdf(file);
      setResult(res);
      setTab("markdown");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Erreur de connexion au serveur.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--color-bg)", color: "var(--color-text)" }}>
      {/* Header */}
      <header className="border-b px-6 py-4" style={{ borderColor: "var(--color-border)" }}>
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold" style={{ color: "var(--color-primary-light)" }}>
            LEXIS-X5
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>
            Document Intelligence Agentique pour la SST
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 px-6 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Zone Drop */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            className="rounded-lg border-2 border-dashed p-10 text-center cursor-pointer transition-colors"
            style={{
              borderColor: dragging ? "var(--color-primary-light)" : "var(--color-border)",
              background: dragging ? "rgba(13,148,136,0.08)" : "var(--color-surface)",
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />
            <Upload className="mx-auto mb-3" size={36} style={{ color: "var(--color-primary)" }} />
            {file ? (
              <div className="flex items-center justify-center gap-2">
                <FileText size={18} style={{ color: "var(--color-primary-light)" }} />
                <span className="font-medium">{file.name}</span>
                <span className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                  ({(file.size / 1024 / 1024).toFixed(1)} MB)
                </span>
              </div>
            ) : (
              <>
                <p className="font-medium">Glissez-déposez un PDF ici</p>
                <p className="text-sm mt-1" style={{ color: "var(--color-text-muted)" }}>
                  ou cliquez pour sélectionner (max 50 MB)
                </p>
              </>
            )}
          </div>

          {/* Erreur */}
          {error && (
            <div
              className="flex items-center gap-2 rounded-lg px-4 py-3 text-sm"
              style={{ background: "rgba(239,68,68,0.12)", color: "#f87171" }}
            >
              <AlertCircle size={18} />
              {error}
            </div>
          )}

          {/* Bouton */}
          <button
            onClick={onSubmit}
            disabled={!file || loading}
            className="w-full rounded-lg px-6 py-3 font-semibold text-white transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ background: !file || loading ? "var(--color-surface-hover)" : "var(--color-primary)" }}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="animate-spin" size={18} />
                Analyse en cours...
              </span>
            ) : (
              "Analyser le document"
            )}
          </button>

          {/* Résultat */}
          {result && (
            <div className="rounded-lg border" style={{ borderColor: "var(--color-border)", background: "var(--color-surface)" }}>
              {/* Métadonnées */}
              <div
                className="flex flex-wrap gap-6 px-5 py-4 border-b text-sm"
                style={{ borderColor: "var(--color-border)" }}
              >
                <div className="flex items-center gap-2">
                  <BookOpen size={16} style={{ color: "var(--color-primary-light)" }} />
                  <span style={{ color: "var(--color-text-muted)" }}>Pages</span>
                  <span className="font-semibold">{result.pages}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Table size={16} style={{ color: "var(--color-primary-light)" }} />
                  <span style={{ color: "var(--color-text-muted)" }}>Tableaux</span>
                  <span className="font-semibold">{result.tables_count}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Layers size={16} style={{ color: "var(--color-primary-light)" }} />
                  <span style={{ color: "var(--color-text-muted)" }}>Éléments</span>
                  <span className="font-semibold">{result.elements_count}</span>
                </div>
              </div>

              {/* Onglets */}
              <div className="flex border-b" style={{ borderColor: "var(--color-border)" }}>
                <button
                  onClick={() => setTab("markdown")}
                  className="px-5 py-2.5 text-sm font-medium transition-colors"
                  style={{
                    borderBottom: tab === "markdown" ? "2px solid var(--color-primary-light)" : "2px solid transparent",
                    color: tab === "markdown" ? "var(--color-primary-light)" : "var(--color-text-muted)",
                  }}
                >
                  Markdown
                </button>
                <button
                  onClick={() => setTab("json")}
                  className="px-5 py-2.5 text-sm font-medium transition-colors"
                  style={{
                    borderBottom: tab === "json" ? "2px solid var(--color-primary-light)" : "2px solid transparent",
                    color: tab === "json" ? "var(--color-primary-light)" : "var(--color-text-muted)",
                  }}
                >
                  JSON
                </button>
              </div>

              {/* Contenu */}
              <div className="p-5 overflow-auto max-h-[600px]">
                {tab === "markdown" ? (
                  <pre className="whitespace-pre-wrap text-sm leading-relaxed font-mono" style={{ color: "var(--color-text)" }}>
                    {result.markdown}
                  </pre>
                ) : (
                  <pre className="whitespace-pre-wrap text-sm leading-relaxed font-mono" style={{ color: "var(--color-text)" }}>
                    {JSON.stringify(result.json_data, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t px-6 py-3 text-center text-xs" style={{ borderColor: "var(--color-border)", color: "var(--color-text-muted)" }}>
        LEXIS-X5 &middot; Preventera / AgenticX5 &middot; Loi 25 conforme
      </footer>
    </div>
  );
}

export default App;
