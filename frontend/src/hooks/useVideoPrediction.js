import { useState, useCallback } from 'react';
import { predictVideo } from '../services/api';

export const STATES = {
  IDLE: 'idle',
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  SUCCESS: 'success',
  ERROR: 'error',
};

export function useVideoPrediction() {
  const [state, setState] = useState(STATES.IDLE);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (file) => {
    setState(STATES.UPLOADING);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      setState(STATES.PROCESSING);

      const data = await predictVideo(file, (percent) => {
        setProgress(percent);
        if (percent >= 100) {
          setState(STATES.PROCESSING);
        }
      });

      setResult(data);
      setState(STATES.SUCCESS);
    } catch (err) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        'Analysis failed. Please try again.';
      setError(message);
      setState(STATES.ERROR);
    }
  }, []);

  const reset = useCallback(() => {
    setState(STATES.IDLE);
    setProgress(0);
    setResult(null);
    setError(null);
  }, []);

  return { state, progress, result, error, analyze, reset };
}