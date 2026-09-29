import axios from 'axios';

const api = axios.create({
  baseURL: 'https://realeyes-api-yu1x.onrender.com/api/v1',
  timeout: 120000,
});

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const predictVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });

  return response.data;
};

export const fetchRecentReports = async () => {
  const response = await api.get('/reports');
  return response.data;
};

export const fetchReportById = async (reportId) => {
  const response = await api.get(`/reports/${reportId}`);
  return response.data;
};

export const seedSampleReports = async () => {
  const response = await api.get('/reports/seed');
  return response.data;
};

export default api;