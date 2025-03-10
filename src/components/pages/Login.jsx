import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

const Login = ({ onLogin }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const API_URL = process.env.REACT_APP_API_URL;

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch(`${API_URL}/token`, {
                method: "POST",
                body: new URLSearchParams({ username: email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Ошибка входа");
            }

            localStorage.setItem("token", data.access_token);
            onLogin();
            navigate("/");
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Вход</h2>
                {error && <p className="error">{error}</p>}
                <form onSubmit={handleSubmit}>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit" className="login-btn">Войти</button>
                </form>
                <p className="register-text">
                    Еще нет аккаунта?{" "}
                    <span className="register-link" onClick={() => navigate("/register")}>
                        Зарегистрироваться
                    </span>
                </p>
            </div>
        </div>
    );
};

export default Login;
