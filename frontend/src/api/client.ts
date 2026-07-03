import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const uploadImages = async (imageA: File, imageB: File) => {
    const formData = new FormData();
    formData.append('image_a', imageA);
    formData.append('image_b', imageB);

    const response = await apiClient.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const compareImages = async (resultId: string) => {
    const response = await apiClient.post(`/compare/${resultId}`);
    return response.data;
};

export const getResult = async (resultId: string) => {
    const response = await apiClient.get(`/results/${resultId}`);
    return response.data;
};

export const getReportUrl = (resultId: string) => {
    return `${API_URL}/report/${resultId}`;
};

export const getAssetUrl = (urlPath: string) => {
    if (!urlPath) return '';
    return `http://localhost:8000${urlPath}`;
};
