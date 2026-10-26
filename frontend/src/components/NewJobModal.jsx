import { useState } from "react";
import Modal from "./Modal";
import TagInput from "./TagInput";
import ErrorBanner from "./ErrorBanner";
import { jobsApi, apiErrorMessage } from "../api/client";

const EDUCATION_OPTIONS = ["Any", "Diploma", "Bachelor's", "Master's", "PhD"];

export default function NewJobModal({ onClose, onCreated }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState([]);
  const [preferredSkills, setPreferredSkills] = useState([]);
  const [minExperience, setMinExperience] = useState(0);
  const [education, setEducation] = useState("Any");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (title.trim().length < 2) {
      setError("Please enter a job title.");
      return;
    }
    if (description.trim().length < 10) {
      setError("Please enter a fuller job description (at least a sentence or two).");
      return;
    }

    setSubmitting(true);
    try {
      const job = await jobsApi.create({
        title: title.trim(),
        description: description.trim(),
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        min_experience: Number(minExperience) || 0,
        education_requirement: education,
      });
      onCreated(job);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not create job. Please check the fields and try again."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Modal title="Create a new job" onClose={onClose} wide>
      <form onSubmit={handleSubmit} className="space-y-4">
        <ErrorBanner message={error} />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Job title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Java Backend Developer"
            className="w-full rounded-lg border border-border px-3 py-2.5 text-sm outline-none focus:border-teal"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-ink">Job description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            placeholder="Describe the role, responsibilities, and what the ideal candidate will do…"
            className="w-full rounded-lg border border-border px-3 py-2.5 text-sm outline-none focus:border-teal"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">Required skills</label>
            <TagInput value={requiredSkills} onChange={setRequiredSkills} placeholder="Type a skill, press Enter" />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">Preferred skills</label>
            <TagInput value={preferredSkills} onChange={setPreferredSkills} placeholder="Type a skill, press Enter" />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">Minimum experience (years)</label>
            <input
              type="number"
              min={0}
              max={50}
              step={0.5}
              value={minExperience}
              onChange={(e) => setMinExperience(e.target.value)}
              className="w-full rounded-lg border border-border px-3 py-2.5 text-sm outline-none focus:border-teal"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-ink">Education requirement</label>
            <select
              value={education}
              onChange={(e) => setEducation(e.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2.5 text-sm outline-none focus:border-teal"
            >
              {EDUCATION_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2.5 text-sm font-medium text-muted hover:bg-surface"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-deepblue px-5 py-2.5 text-sm font-semibold text-white hover:bg-navy disabled:opacity-50"
          >
            {submitting ? "Creating…" : "Create job"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
