import { useEffect, useRef, useState } from "react";

export function useAutoSave<T>(key: string, data: T, delay = 500) {
  const [saved, setSaved] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      try {
        localStorage.setItem(key, JSON.stringify(data));
        setSaved(true);
        const resetTimer = setTimeout(() => setSaved(false), 2000);
        return () => clearTimeout(resetTimer);
      } catch {
        // storage full or unavailable
      }
    }, delay);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [key, data, delay]);

  const clearDraft = () => {
    try {
      localStorage.removeItem(key);
    } catch {
      // ignore
    }
  };

  const restoreDraft = (): T | null => {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return null;
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  };

  return { saved, clearDraft, restoreDraft };
}
