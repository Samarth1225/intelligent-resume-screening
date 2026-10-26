import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("irscs_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("irscs_token");
      localStorage.removeItem("irscs_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

function apiErrorMessage(error, fallback = "Something went wrong. Please try again.") {
  return error?.response?.data?.detail || error?.message || fallback;
}

export const jobsApi = {
  list: () => api.get("/api/jobs").then((r) => r.data),
  get: (id) => api.get(`/api/jobs/${id}`).then((r) => r.data),
  create: (payload) => api.post("/api/jobs", payload).then((r) => r.data),
  remove: (id) => api.delete(`/api/jobs/${id}`),
  uploadResumes: (id, files, onUploadProgress) => {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return api
      .post(`/api/jobs/${id}/resumes`, form, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress,
      })
      .then((r) => r.data);
  },
  candidates: (id, params) => api.get(`/api/jobs/${id}/candidates`, { params }).then((r) => r.data),
  rankings: (id) => api.get(`/api/jobs/${id}/rankings`).then((r) => r.data),
};

export const candidatesApi = {
  get: (id) => api.get(`/api/candidates/${id}`).then((r) => r.data),
  analyze: (id) => api.post(`/api/candidates/${id}/analyze`).then((r) => r.data),
};

export const authApi = {
  login: (email, password) => api.post("/api/auth/login", { email, password }).then((r) => r.data),
};

export const metaApi = {
  get: () => api.get("/api/meta").then((r) => r.data),
};

export { apiErrorMessage };
