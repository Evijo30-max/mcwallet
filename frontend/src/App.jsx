
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";

import Login from "./pages/auth/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import UserLayout from "./layouts/UserLayout";

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Chargement...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Page publique */}
      <Route path="/login" element={<Login />} />

      {/* Zone utilisateur */}
      <Route
        element={
          <ProtectedRoute>
            <UserLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />

        {/* Pages que nous allons construire ensuite */}
        <Route path="/accounts" element={<div>Mes comptes</div>} />
        <Route path="/transactions" element={<div>Transactions</div>} />
        <Route path="/deposit" element={<div>Déposer</div>} />
        <Route path="/withdraw" element={<div>Retirer</div>} />
        <Route path="/convert" element={<div>Convertir</div>} />
        <Route path="/profile" element={<div>Profil</div>} />
      </Route>

      {/* Toute URL inconnue */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
