import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Users, Gauge, Trophy, ArrowRight, Trash2 } from "lucide-react";
import Layout from "../components/Layout";
import StatCard from "../components/StatCard";
import EmptyState from "../components/EmptyState";
import LoadingSpinner from "../components/LoadingSpinner";
import NewJobModal from "../components/NewJobModal";
import { jobsApi, apiErrorMessage } from "../api/client";
import DeleteJobModal from "../components/DeleteJobModal";

export default function DashboardPage() {
  const [jobs, setJobs] = useState(null);
  const [error, setError] = useState("");
  const [showNewJob, setShowNewJob] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setError("");
    try {
      const data = await jobsApi.list();
      setJobs(data);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not load jobs."));
    }
  }

  const totals = (jobs || []).reduce(
    (acc, j) => {
      acc.candidates += j.stats.total_candidates;
      acc.processed += j.stats.resumes_processed;
      acc.above80 += j.stats.candidates_above_80;
      if (j.stats.total_candidates > 0) {
        acc.weightedScoreSum += j.stats.average_match_score * j.stats.total_candidates;
        acc.weightedCount += j.stats.total_candidates;
      }
      return acc;
    },
    { candidates: 0, processed: 0, above80: 0, weightedScoreSum: 0, weightedCount: 0 }
  );
  const avgScore = totals.weightedCount ? Math.round(totals.weightedScoreSum / totals.weightedCount) : 0;

  return (
    <Layout
      title="Dashboard"
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
        <LoadingSpinner label="Loading dashboard…" />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard label="Open Jobs" value={jobs.length} />
            <StatCard label="Total Candidates" value={totals.candidates} />
            <StatCard label="Resumes Processed" value={totals.processed} />
            <StatCard label="Avg. Match Score" value={`${avgScore}%`} />
          </div>

          <div className="mt-8">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-lg font-semibold text-ink">Your jobs</h2>
              {jobs.length > 0 && (
                <button onClick={() => navigate("/jobs")} className="text-sm font-medium text-deepblue hover:underline">
                  View all
                </button>
              )}
            </div>

            {jobs.length === 0 ? (
              <EmptyState
                title="No jobs yet"
                description="Create your first job to start uploading resumes and ranking candidates."
                action={
                  <button
                    onClick={() => setShowNewJob(true)}
                    className="rounded-lg bg-deepblue px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy"
                  >
                    Create a job
                  </button>
                }
              />
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {jobs.slice(0, 6).map((job) => (
                    <JobCard key={job.id} job={job} onClick={() => navigate(`/jobs/${job.id}`)}
           onDeleted={() => setJobs((prev) => prev.filter((j) => j.id !== job.id))} />
                ))}
              </div>
            )}
          </div>
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

export function JobCard({ job, onClick, onDeleted }) {
  const [showDelete, setShowDelete] = useState(false);
  return (
    <div className="relative">
      <button
        onClick={onClick}
        className="flex h-full w-full flex-col rounded-xl border border-border bg-white p-5 text-left transition-shadow hover:shadow-md"
      >
        <h3 className="pr-8 font-display text-base font-semibold text-ink">{job.title}</h3>
        <p className="mt-1 text-xs text-muted">
          {job.education_requirement} · Min {job.min_experience} yrs experience
        </p>

        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <MiniStat icon={Users} value={job.stats.total_candidates} label="Candidates" />
          <MiniStat icon={Gauge} value={`${job.stats.average_match_score}%`} label="Avg score" />
          <MiniStat icon={Trophy} value={job.stats.candidates_above_80} label="Above 80%" />
        </div>

        <span className="mt-4 flex items-center gap-1 text-sm font-medium text-deepblue">
          View ranking <ArrowRight size={14} />
        </span>
      </button>

      <button
        onClick={() => setShowDelete(true)}
        aria-label={`Delete ${job.title}`}
        title="Delete job"
        className="absolute right-3 top-3 rounded-lg p-1.5 text-muted hover:bg-bad-bg hover:text-bad"
      >
        <Trash2 size={16} />
      </button>

      {showDelete && (
        <DeleteJobModal
          job={job}
          onClose={() => setShowDelete(false)}
          onDeleted={() => {
            setShowDelete(false);
            onDeleted?.(job);
          }}
        />
      )}
    </div>
  );
}

function MiniStat({ icon: Icon, value, label }) {
  return (
    <div className="rounded-lg bg-surface px-2 py-2.5">
      <Icon size={14} className="mx-auto mb-1 text-teal" />
      <p className="text-sm font-semibold text-ink">{value}</p>
      <p className="text-[10px] text-muted">{label}</p>
    </div>
  );
}
