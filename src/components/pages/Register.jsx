import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";

const Register = ({ onRegister }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const API_URL = process.env.REACT_APP_API_URL;

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch(`${API_URL}/register/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Ошибка регистрации");
            }

            const loginResponse = await fetch(`${API_URL}/token`, {
                method: "POST",
                body: new URLSearchParams({ username: email, password }),
            });

            if (!loginResponse.ok) {
                const loginData = await loginResponse.json();
                throw new Error(loginData.detail || "Ошибка входа после регистрации");
            }

            const loginData = await loginResponse.json();
            localStorage.setItem("token", loginData.access_token);
            onRegister();
            navigate("/");
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="register-wrapper">
            <div className="register-container">
                <h2>Регистрация</h2>
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
                    <button type="submit">Зарегистрироваться</button>
                </form>
            </div>
        </div>
    );
};

export default Register;
