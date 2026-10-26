import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Search } from "lucide-react";
import Layout from "../components/Layout";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";
import NewJobModal from "../components/NewJobModal";
import { JobCard } from "./DashboardPage";
import { jobsApi, apiErrorMessage } from "../api/client";

export default function JobsPage() {
  const [jobs, setJobs] = useState(null);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [showNewJob, setShowNewJob] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    jobsApi
      .list()
      .then(setJobs)
      .catch((err) => setError(apiErrorMessage(err, "Could not load jobs.")));
  }, []);

  const filtered = useMemo(() => {
    if (!jobs) return [];
    if (!search.trim()) return jobs;
    return jobs.filter((j) => j.title.toLowerCase().includes(search.toLowerCase()));
  }, [jobs, search]);

  return (
    <Layout
      title="Jobs"
      actions={
        <button
          onClick={() => setShowNewJob(true)}
          className="flex items-center gap-1.5 rounded-lg bg-deepblue px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy"
        >
          <Plus size={16} /> New Job
        </button>
      }
    >
      {error && <p className="mb-4 text-sm text-bad">{error}</p>}

      {jobs === null ? (
        <LoadingSpinner label="Loading jobs…" />
      ) : (
        <>
          {jobs.length > 0 && (
            <div className="relative mb-5 max-w-sm">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search jobs by title…"
                className="w-full rounded-lg border border-border bg-white py-2.5 pl-9 pr-3 text-sm outline-none focus:border-teal"
              />
            </div>
          )}

          {filtered.length === 0 ? (
            <EmptyState
              title={jobs.length === 0 ? "No jobs yet" : "No jobs match your search"}
              description={
                jobs.length === 0
                  ? "Create your first job to start uploading resumes and ranking candidates."
                  : "Try a different search term."
              }
              action={
                jobs.length === 0 && (
                  <button
                    onClick={() => setShowNewJob(true)}
                    className="rounded-lg bg-deepblue px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy"
                  >
                    Create a job
                  </button>
                )
              }
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {filtered.map((job) => (
               <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)}
         onDeleted={() => setJobs((prev) => prev.filter((j) => j.id !== job.id))} />
              ))}
            </div>
          )}
        </>
      )}

      {showNewJob && (
        <NewJobModal
          onClose={() => setShowNewJob(false)}
          onCreated={(job) => {
            setShowNewJob(false);
            navigate(`/jobs/${job.id}`);
          }}
        />
      )}
    </Layout>
  );
}
