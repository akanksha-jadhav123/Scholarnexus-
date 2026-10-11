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

// ---------- AUTH ----------
export const registerUser = (data) => api.post("/auth/register", data);
export const loginUser = (data) => api.post("/auth/login", data);

// ---------- PROFILE ----------
export const getProfile = () => api.get("/profile/");
export const saveProfile = (data) => api.post("/profile/", data);
export const getProfileCompletion = () => api.get("/profile/completion");

// ---------- SCHOLARSHIPS ----------
export const listScholarships = () => api.get("/scholarships/");
export const searchScholarships = (params) => api.get("/scholarships/search", { params });
export const getScholarship = (id) => api.get(`/scholarships/${id}`);
export const checkEligibility = (id) => api.get(`/scholarships/${id}/eligibility`);
export const getRecommendations = () => api.get("/scholarships/recommendations");
export const compareScholarships = (ids) => api.post("/scholarships/compare", { scholarship_ids: ids });
export const toggleBookmark = (id) => api.post(`/scholarships/bookmark/${id}`);
export const getBookmarks = () => api.get("/scholarships/bookmarks");
export const getUpcomingDeadlines = () => api.get("/scholarships/upcoming-deadlines");

// ---------- HEALTH ----------
export const healthCheck = () => api.get("/health");

// ---------- APPLICATIONS ----------
export const listApplications = () => api.get("/applications/");
export const saveApplication = (data) => api.post("/applications/", data);
export const deleteApplication = (id) => api.delete(`/applications/${id}`);

// ---------- DOCUMENTS ----------
export const getDocumentChecklist = (id) => api.get(`/documents/${id}`);
export const updateDocument = (id, data) => api.post(`/documents/${id}`, data);

// ---------- NOTIFICATIONS ----------
export const listNotifications = () => api.get("/notifications/");
export const markNotificationRead = (id) => api.post(`/notifications/${id}/read`);
export const markAllNotificationsRead = () => api.post("/notifications/read-all");

// ---------- ADMIN ----------
export const getAdminAnalytics = () => api.get("/admin/analytics");
export const getAdminUsers = () => api.get("/admin/users");
export const updateUserRole = (userId, role) => api.put(`/admin/users/${userId}/role`, { role });
export const verifyScholarship = (id) => api.post(`/admin/scholarships/${id}/verify`);
export const deleteScholarship = (id) => api.delete(`/admin/scholarships/${id}`);

// ---------- CRAWLER / SCRAPER ----------
export const getCrawlerSources = () => api.get("/crawler/sources");
export const getCrawlerStats = () => api.get("/crawler/stats");
export const runCrawlerSync = () => api.post("/crawler/sync");

export default api;