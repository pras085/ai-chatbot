import React, { Suspense, lazy } from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import useUser from './hooks/useUser';
import { FeatureProvider } from "./contexts/FeatureContext";
import "./styles/App.css";
import "highlight.js/styles/sunburst.css";
import AdminPage from "./pages/AdminPage";
import FloatingHomeButton from "./components/FloatingHomeButton";
import NavigationBar from "./components/Navbar";

const LoginPage = lazy(() => import("./pages/LoginPage"));
const HomePage = lazy(() => import("./pages/HomePage"));
const ChatListPage = lazy(() => import("./pages/ChatListPage"));
const ChatPage = lazy(() => import("./pages/ChatPage"));

function PrivateRoute({ children }) {
  const { user, loading } = useUser();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useUser();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (user) {
    return <Navigate to="/home" replace />;
  }

  return children;
}

function App() {
  return (
    <Router>
      <ErrorBoundary>
        <Suspense fallback={<div>Loading...</div>}>
          <FeatureProvider>
            <div className="App">
              <main>
                <NavigationBar />
                <Routes>
                  <Route path="/login" element={
                    <PublicRoute>
                      <LoginPage />
                    </PublicRoute>
                  } />
                  <Route path="/home" element={
                    <PrivateRoute>
                      <HomePage />
                    </PrivateRoute>
                  } />
                  <Route path="/chats" element={
                    <PrivateRoute>
                      <ChatListPage />
                    </PrivateRoute>
                  } />
                  <Route path="/chat/:chatId" element={
                    <PrivateRoute>
                      <ChatPage />
                    </PrivateRoute>
                  } />
                  <Route path="/admin" element={
                    <PrivateRoute>
                      <AdminPage />
                    </PrivateRoute>
                  } />
                  <Route path="/" element={<Navigate to="/home" replace />} />
                  <Route path="*" element={<Navigate to="/home" replace />} />
                </Routes>
                {/* <FloatingHomeButton /> */}
              </main>
            </div>
          </FeatureProvider>
        </Suspense>
      </ErrorBoundary>
    </Router>
  );
}

export default App;