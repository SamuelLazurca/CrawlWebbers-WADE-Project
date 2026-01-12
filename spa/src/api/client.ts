import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
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
    console.error(`Error fetching ${url}:`, error);
    return { success: false, data: null, error: String(error) };
  }
};
