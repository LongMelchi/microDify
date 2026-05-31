/**
 * General utility functions.
 * TODO: add formatting, validation, or helper utilities as needed.
 */

/**
 * Format a date string or timestamp into a human-readable form.
 */
export function formatDate(date: string | number | Date): string {
  const d = typeof date === "string" || typeof date === "number" ? new Date(date) : date;
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Truncate a string to a given length, appending ellipsis if truncated.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + "...";
}
