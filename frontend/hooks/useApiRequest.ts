import { useState, useCallback } from 'react';

type RequestState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

/**
 * Hook для упрощения API запросов
 * Управляет состояниями loading, error, data
 */
export function useApiRequest<T>() {
  const [state, setState] = useState<RequestState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (apiCall: () => Promise<T>) => {
    setState({ data: null, loading: true, error: null });

    try {
      const result = await apiCall();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Произошла ошибка';
      setState({ data: null, loading: false, error: errorMessage });
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

/**
 * Hook для мутаций (POST, PUT, DELETE)
 */
export function useMutation<T, P = void>() {
  const [state, setState] = useState<RequestState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const mutate = useCallback(async (apiCall: (params: P) => Promise<T>, params: P) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const result = await apiCall(params);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (err: any) {
      const errorMessage = err.message || 'Произошла ошибка';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    mutate,
    reset,
  };
}
