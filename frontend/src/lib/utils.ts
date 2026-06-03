/**
 * General utility functions.
 * TODO: add formatting, validation, or helper utilities as needed.
 */

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

/**
 * Format a date string/timestamp as ``YYYY-MM-DD``.
 * Returns the original input unchanged if it cannot be parsed.
 */
export function formatDate(date: string | number | Date): string {
  try {
    const d = typeof date === "string" || typeof date === "number" ? new Date(date) : date;
    if (Number.isNaN(d.getTime())) return String(date);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  } catch {
    return String(date);
  }
}

/**
 * Format a date string/timestamp as ``YYYY-MM-DD HH:mm:ss``.
 * Returns the original input unchanged if it cannot be parsed.
 */
export function formatDateTime(date: string | number | Date): string {
  try {
    const d = typeof date === "string" || typeof date === "number" ? new Date(date) : date;
    if (Number.isNaN(d.getTime())) return String(date);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  } catch {
    return String(date);
  }
}

/**
 * Truncate a string to a given length, appending ellipsis if truncated.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + "...";
}
