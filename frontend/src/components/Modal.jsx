import { X } from "lucide-react";

export default function Modal({ title, onClose, children, wide }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink/50 px-4 py-8 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className={`w-full ${wide ? "max-w-2xl" : "max-w-lg"} rounded-2xl bg-white shadow-xl`}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="font-display text-lg font-semibold text-ink">{title}</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted hover:bg-surface hover:text-ink"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>
        <div className="max-h-[75vh] overflow-y-auto px-6 py-5">{children}</div>
      </div>
    </div>
  );
}
