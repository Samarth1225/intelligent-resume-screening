import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import JobsPage from "./pages/JobsPage";
import JobDetailPage from "./pages/JobDetailPage";
import CandidateDetailPage from "./pages/CandidateDetailPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<LoginPage />} />

        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/jobs" element={<ProtectedRoute><JobsPage /></ProtectedRoute>} />
        <Route path="/jobs/:jobId" element={<ProtectedRoute><JobDetailPage /></ProtectedRoute>} />
        {/* Alias -- ranking table lives on the job detail page itself */}
        <Route path="/jobs/:jobId/candidates" element={<ProtectedRoute><JobDetailPage candidatesOnly /></ProtectedRoute>} />
        <Route path="/candidates/:candidateId" element={<ProtectedRoute><CandidateDetailPage /></ProtectedRoute>} />

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
