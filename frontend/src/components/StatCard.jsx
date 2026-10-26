export default function StatCard({ label, value, hint }) {
  return (
    <div className="rounded-xl border border-border bg-white p-4">
      <p className="font-display text-3xl font-semibold text-deepblue">{value}</p>
      <p className="mt-1 text-sm text-muted">{label}</p>
      {hint && <p className="mt-0.5 text-xs text-muted/80">{hint}</p>}
    </div>
  );
}
