import { useState } from "react";
import Modal from "./Modal";
import ErrorBanner from "./ErrorBanner";
import { jobsApi, apiErrorMessage } from "../api/client";

export default function DeleteJobModal({ job, onClose, onDeleted }) {
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");
  const count = job.stats?.total_candidates ?? 0;

  async function confirmDelete() {
    setDeleting(true);
    setError("");
    try {
      await jobsApi.remove(job.id);
      onDeleted();
    } catch (err) {
      setError(apiErrorMessage(err, "Could not delete this job. Please try again."));
      setDeleting(false);
    }
  }

  return (
    <Modal title="Delete this job?" onClose={deleting ? () => {} : onClose}>
      <div className="space-y-4">
        <ErrorBanner message={error} />
        <p className="text-sm text-ink">
          “{job.title}” will be permanently deleted
          {count > 0 ? `, along with its ${count} candidate${count === 1 ? "" : "s"} and their uploaded resumes` : ""}.
          This can't be undone.
        </p>
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            disabled={deleting}
            className="rounded-lg px-4 py-2.5 text-sm font-medium text-muted hover:bg-surface disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={confirmDelete}
            disabled={deleting}
            className="rounded-lg bg-bad px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50"
          >
            {deleting ? "Deleting…" : "Delete job"}
          </button>
        </div>
      </div>
    </Modal>
  );
}