import { useState } from "react";
import { X } from "lucide-react";

export default function TagInput({ value, onChange, placeholder }) {
  const [draft, setDraft] = useState("");

  function commit() {
    const cleaned = draft.trim();
    if (cleaned && !value.some((v) => v.toLowerCase() === cleaned.toLowerCase())) {
      onChange([...value, cleaned]);
    }
    setDraft("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      commit();
    } else if (e.key === "Backspace" && !draft && value.length > 0) {
      onChange(value.slice(0, -1));
    }
  }

  return (
    <div className="flex min-h-11 flex-wrap items-center gap-1.5 rounded-lg border border-border bg-white px-2.5 py-1.5 focus-within:border-teal">
      {value.map((tag) => (
        <span
          key={tag}
          className="flex items-center gap-1 rounded-full bg-[#eef3f7] px-2.5 py-1 text-xs font-medium text-ink"
        >
          {tag}
          <button
            type="button"
            onClick={() => onChange(value.filter((v) => v !== tag))}
            className="text-muted hover:text-bad"
            aria-label={`Remove ${tag}`}
          >
            <X size={12} />
          </button>
        </span>
      ))}
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={handleKeyDown}
        onBlur={commit}
        placeholder={value.length === 0 ? placeholder : ""}
        className="min-w-[120px] flex-1 border-none bg-transparent py-1 text-sm outline-none placeholder:text-muted/70"
      />
    </div>
  );
}
