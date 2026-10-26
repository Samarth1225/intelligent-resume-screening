import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileText, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { jobsApi, apiErrorMessage } from "../api/client";

const STAGES = ["Uploading…", "Extracting text…", "Analyzing resume…", "Calculating match…"];
const STAGE_MS = 550;
const ACCEPTED = [".pdf", ".docx"];

function extOf(filename) {
  const idx = filename.lastIndexOf(".");
  return idx === -1 ? "" : filename.slice(idx).toLowerCase();
}

export default function UploadDropzone({ jobId, onUploaded }) {
  const [files, setFiles] = useState([]); // { file, key }
  const [rowState, setRowState] = useState({}); // key -> { stageIndex, done, status, message, score }
  const [isSubmitting, setSubmitting] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [formError, setFormError] = useState("");
  const inputRef = useRef(null);

  const addFiles = useCallback((fileList) => {
    const accepted = [];
    const rejected = [];
    Array.from(fileList).forEach((file) => {
      if (ACCEPTED.includes(extOf(file.name))) {
        accepted.push({ file, key: `${file.name}-${file.size}-${file.lastModified}` });
      } else {
        rejected.push(file.name);
      }
    });
    setFiles((prev) => {
      const existingKeys = new Set(prev.map((f) => f.key));
      return [...prev, ...accepted.filter((f) => !existingKeys.has(f.key))];
    });
    setFormError(rejected.length ? `Unsupported file type — skipped: ${rejected.join(", ")}` : "");
  }, []);

  function removeFile(key) {
    setFiles((prev) => prev.filter((f) => f.key !== key));
    setRowState((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  async function handleSubmit() {
    if (files.length === 0 || isSubmitting) return;
    setSubmitting(true);
    setFormError("");

    const initial = {};
    files.forEach((f) => {
      initial[f.key] = { stageIndex: 0, done: false, status: null, message: null, score: null };
    });
    setRowState(initial);

    // Staged visual progression, independent of the real request timing —
    // gives the recruiter the "Uploading… / Extracting… / Analyzing… /
    // Calculating…" feedback called for in the spec even though the backend
    // actually processes each batch in one request.
    let stageIndex = 0;
    const ticker = setInterval(() => {
      stageIndex = Math.min(stageIndex + 1, STAGES.length - 1);
      setRowState((prev) => {
        const next = { ...prev };
        for (const key of Object.keys(next)) {
          if (!next[key].done) next[key] = { ...next[key], stageIndex };
        }
        return next;
      });
    }, STAGE_MS);

    const minWait = new Promise((resolve) => setTimeout(resolve, STAGE_MS * (STAGES.length - 1)));

    try {
      const [results] = await Promise.all([
        jobsApi.uploadResumes(jobId, files.map((f) => f.file)),
        minWait,
      ]);
      clearInterval(ticker);

      setRowState((prev) => {
        const next = { ...prev };
        files.forEach((f, idx) => {
          const result = results[idx] || results.find((r) => r.filename === f.file.name);
          next[f.key] = {
            stageIndex: STAGES.length - 1,
            done: true,
            status: result?.status || "failed",
            message: result?.message || null,
            score: result?.overall_score ?? null,
          };
        });
        return next;
      });

      onUploaded?.(results);
    } catch (err) {
      clearInterval(ticker);
      setFormError(apiErrorMessage(err, "Upload failed. Please try again."));
      setRowState((prev) => {
        const next = { ...prev };
        for (const key of Object.keys(next)) {
          next[key] = { ...next[key], done: true, status: "failed", message: "Request failed" };
        }
        return next;
      });
    } finally {
      setSubmitting(false);
    }
  }

  function resetAll() {
    setFiles([]);
    setRowState({});
    setFormError("");
  }

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          addFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
          dragOver ? "border-teal bg-[#eef7f6]" : "border-border bg-white hover:border-teal/60"
        }`}
      >
        <UploadCloud className="mb-3 text-teal" size={30} />
        <p className="text-sm font-medium text-ink">Drag and drop resumes here, or click to browse</p>
        <p className="mt-1 text-xs text-muted">Supports multiple files · PDF or DOCX · up to 10MB each</p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      {formError && <p className="mt-2 text-sm text-bad">{formError}</p>}

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map(({ file, key }) => {
            const state = rowState[key];
            return (
              <div
                key={key}
                className="flex items-center justify-between gap-3 rounded-lg border border-border bg-white px-4 py-3"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <FileText size={18} className="shrink-0 text-deepblue" />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-ink">{file.name}</p>
                    {state && (
                      <p className="text-xs text-muted">
                        {state.done
                          ? state.status === "completed"
                            ? `Completed · Match score ${state.score}%`
                            : state.message || "Processing failed"
                          : STAGES[state.stageIndex]}
                      </p>
                    )}
                  </div>
                </div>

                {!state && !isSubmitting && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(key);
                    }}
                    className="shrink-0 text-xs font-medium text-muted hover:text-bad"
                  >
                    Remove
                  </button>
                )}
                {state && !state.done && <Loader2 size={18} className="shrink-0 animate-spin text-teal" />}
                {state?.done && state.status === "completed" && (
                  <CheckCircle2 size={18} className="shrink-0 text-good" />
                )}
                {state?.done && state.status !== "completed" && (
                  <XCircle size={18} className="shrink-0 text-bad" />
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="mt-4 flex justify-end gap-2">
        {files.length > 0 && (
          <button
            onClick={resetAll}
            disabled={isSubmitting}
            className="rounded-lg px-4 py-2 text-sm font-medium text-muted hover:bg-surface disabled:opacity-50"
          >
            Clear
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={files.length === 0 || isSubmitting}
          className="rounded-lg bg-deepblue px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-navy disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Processing…" : `Upload & analyze ${files.length || ""} resume${files.length === 1 ? "" : "s"}`}
        </button>
      </div>
    </div>
  );
}
