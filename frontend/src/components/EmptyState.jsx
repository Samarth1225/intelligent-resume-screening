export default function EmptyState({ title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-white px-6 py-14 text-center">
      <h3 className="font-display text-lg font-semibold text-ink">{title}</h3>
      {description && <p className="mt-1.5 max-w-sm text-sm text-muted">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
