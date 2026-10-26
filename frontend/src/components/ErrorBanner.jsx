import { AlertTriangle } from "lucide-react";

export default function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-bad/30 bg-bad-bg px-4 py-3 text-sm text-bad">
      <AlertTriangle size={16} className="mt-0.5 shrink-0" />
      <span>{message}</span>
    </div>
  );
}
