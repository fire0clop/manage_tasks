import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import TaskForm from "./components/create_task_form/Create_task";
import TaskList from "./components/task_list/List_tasks";
import Login from "./components/pages/Login";
import Register from "./components/pages/Register";

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(() => {
        const token = localStorage.getItem("token");
        console.log("Initial token check:", token); // Логируем начальное значение токена
        return !!token;
    });

    useEffect(() => {
        const token = localStorage.getItem("token");
        console.log("Token on page load:", token); // Логируем токен при загрузке страницы
        setIsAuthenticated(!!token);
    }, []);

    const handleLogin = () => {
        const token = localStorage.getItem("token");
        console.log("User logged in, token:", token);
        setIsAuthenticated(!!token);
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        console.log("User logged out");
        setIsAuthenticated(false);
    };

    console.log("Auth state:", isAuthenticated); // Логируем состояние аутентификации

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login onLogin={handleLogin} />} />
                <Route path="/register" element={<Register onRegister={handleLogin} />} />
                <Route
                    path="/"
                    element={isAuthenticated ? <TaskList onLogout={handleLogout} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/tasks/new"
                    element={isAuthenticated ? <TaskForm /> : <Navigate to="/login" />}
                />
            </Routes>
        </Router>
    );
}

export default App;
