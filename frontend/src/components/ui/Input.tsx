"use client";

import { useState, useRef, useEffect, type InputHTMLAttributes, type TextareaHTMLAttributes } from "react";

/* ── Input ──────────────────────────────────────────── */

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
}

export function Input({
  label,
  hint,
  error,
  required,
  className = "",
  id,
  ...props
}: InputProps) {
  const inputId = id || label?.replace(/\s+/g, "-").toLowerCase();
  return (
    <div className="mb-5 max-w-[480px]">
      {label && (
        <label htmlFor={inputId} className="block text-[14px] font-semibold mb-2">
          {label}
          {required && <span className="text-[var(--color-error)] ml-0.5">*</span>}
        </label>
      )}
      <input
        id={inputId}
        className={`w-full px-3.5 py-2.5 text-[14px] font-sans border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-surface)] text-[var(--color-text)] min-h-[44px] transition-all duration-150 ease-out
          focus:outline-none focus:border-[var(--color-primary)] focus:shadow-[0_0_0_3px_var(--color-primary-light)]
          disabled:bg-[var(--color-bg)] disabled:text-[var(--color-text-tertiary)] disabled:cursor-not-allowed
          ${error ? "border-[var(--color-error)] focus:shadow-[0_0_0_3px_rgba(239,68,68,0.15)]" : ""}
          ${className}`}
        {...props}
      />
      {error && <p className="text-[12px] text-[var(--color-error)] mt-1 font-medium">{error}</p>}
      {hint && !error && <p className="text-[12px] text-[var(--color-text-tertiary)] mt-1">{hint}</p>}
    </div>
  );
}

/* ── Select (custom clay-style dropdown) ────────────── */

interface SelectOption {
  value: string;
  label: string;
  desc?: string;
}

interface SelectProps {
  label?: string;
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  required?: boolean;
  className?: string;
}

export function Select({ label, options, value, onChange, required, className = "" }: SelectProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selected = options.find((o) => o.value === value) || options[0];

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  function handleSelect(opt: SelectOption) {
    onChange?.(opt.value);
    setOpen(false);
  }

  return (
    <div className={`mb-5 max-w-[480px] ${className}`} ref={containerRef}>
      {label && (
        <label className="block text-[14px] font-semibold mb-2">
          {label}
          {required && <span className="text-[var(--color-error)] ml-0.5">*</span>}
        </label>
      )}
      <div className="relative">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="w-full px-3.5 py-2.5 pr-10 text-[14px] font-sans border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-surface)] text-[var(--color-text)] min-h-[44px] text-left transition-all duration-150 ease-out
            hover:border-[var(--color-text-secondary)]
            focus:outline-none focus:border-[var(--color-primary)] focus:shadow-[0_0_0_3px_var(--color-primary-light)]"
        >
          {selected?.label || "请选择"}
          <span className={`absolute right-3.5 top-1/2 -mt-[3px] w-2 h-2 border-r-2 border-b-2 border-[var(--color-text-secondary)] transition-transform duration-200 ${open ? "rotate-[225deg] -mt-[1px]" : "rotate-45"}`} />
        </button>
        {open && (
          <ul
            className="absolute top-[calc(100%+4px)] left-0 right-0 z-50 bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-md)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] list-none max-h-[200px] overflow-y-auto p-1"
          >
            {options.map((opt) => (
              <li
                key={opt.value}
                className={`px-3.5 py-2.5 text-[14px] font-medium rounded-[6px] cursor-pointer transition-colors duration-100
                  hover:bg-[var(--color-primary-light)] hover:text-[var(--color-primary)]
                  ${opt.value === selected?.value ? "bg-[var(--color-primary-light)] text-[var(--color-primary)] font-semibold" : ""}`}
                onMouseDown={(e) => { e.preventDefault(); handleSelect(opt); }}
              >
                {opt.label}
                {opt.desc && (
                  <span className="block text-[12px] text-[var(--color-text-tertiary)] font-normal mt-0.5">
                    {opt.desc}
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

/* ── Textarea ───────────────────────────────────────── */

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
  required?: boolean;
}

export function Textarea({
  label,
  hint,
  error,
  required,
  className = "",
  id,
  ...props
}: TextareaProps) {
  const textareaId = id || label?.replace(/\s+/g, "-").toLowerCase();
  return (
    <div className="mb-5 max-w-[480px]">
      {label && (
        <label htmlFor={textareaId} className="block text-[14px] font-semibold mb-2">
          {label}
          {required && <span className="text-[var(--color-error)] ml-0.5">*</span>}
        </label>
      )}
      <textarea
        id={textareaId}
        className={`w-full px-3.5 py-2.5 text-[14px] font-sans border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-surface)] text-[var(--color-text)] min-h-[100px] transition-all duration-150 ease-out resize-y
          focus:outline-none focus:border-[var(--color-primary)] focus:shadow-[0_0_0_3px_var(--color-primary-light)]
          disabled:bg-[var(--color-bg)] disabled:text-[var(--color-text-tertiary)] disabled:cursor-not-allowed
          ${error ? "border-[var(--color-error)] focus:shadow-[0_0_0_3px_rgba(239,68,68,0.15)]" : ""}
          ${className}`}
        {...props}
      />
      {error && <p className="text-[12px] text-[var(--color-error)] mt-1 font-medium">{error}</p>}
      {hint && !error && <p className="text-[12px] text-[var(--color-text-tertiary)] mt-1">{hint}</p>}
    </div>
  );
}
