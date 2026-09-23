import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  headers: { "Content-Type": "application/json" }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export const registerUser = (data) => api.post("/auth/register", data);
export const loginUser = (data) => api.post("/auth/login", data);
export const getProfile = () => api.get("/profile/");
export const saveProfile = (data) => api.post("/profile/", data);
export const getProfileCompletion = () => api.get("/profile/completion");
export const listScholarships = () => api.get("/scholarships/");
export const searchScholarships = (params) => api.get("/scholarships/search", { params });
export const getScholarship = (id) => api.get(`/scholarships/${id}`);
export const checkEligibility = (id) => api.get(`/scholarships/${id}/eligibility`);
export const getRecommendations = () => api.get("/scholarships/recommendations");
export const compareScholarships = (ids) => api.post("/scholarships/compare", { scholarship_ids: ids });
export const toggleBookmark = (id) => api.post(`/scholarships/bookmark/${id}`);
export const getBookmarks = () => api.get("/scholarships/bookmarks");
export const getUpcomingDeadlines = () => api.get("/scholarships/upcoming-deadlines");
export const healthCheck = () => api.get("/health");

export default api;