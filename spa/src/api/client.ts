import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/',
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY,
  },
});

export type Result<T> =
  | {
      success: true;
      data: T;
      error: null;
    }
  | {
      success: false;
      data: null;
      error: string;
    };

export const safeFetch = async <T>(url: string): Promise<Result<T>> => {
  try {
    const response = await api.get<T>(url);
    return { success: true, data: response.data, error: null };
  } catch (error) {
    return { success: false, data: null, error: String(error) };
  }
};

export const safePost = async <T, U>(
  url: string,
  payload: T
): Promise<Result<U>> => {
  try {
    const response = await api.post<U>(url, payload);
    return { success: true, data: response.data, error: null };
  } catch (error) {
    return { success: false, data: null, error: String(error) };
  }
};
