export default function LoadingSpinner({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-14 text-muted">
      <span
        className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-teal"
        aria-hidden="true"
      />
      <span className="text-sm">{label}</span>
    </div>
  );
}
