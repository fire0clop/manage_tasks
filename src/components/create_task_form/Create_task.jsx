import React, { useState } from "react";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import "./Create_task.css";

const TaskForm = ({ onClose, onTaskCreated }) => {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [deadline, setDeadline] = useState("");

    const API_URL = process.env.REACT_APP_API_URL;

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!title) {
            alert("Пожалуйста, введите название задачи.");
            return;
        }

        const newTask = { title, description, deadline, status: "новая" };
        const token = localStorage.getItem("token");

        if (!token) {
            alert("Ошибка: Токен отсутствует. Авторизуйтесь снова.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}/tasks/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(newTask),
            });

            if (response.ok) {
                onTaskCreated();
                onClose();
            } else {
                console.error("Ошибка при создании задачи:", await response.json());
            }
        } catch (err) {
            console.error("Ошибка сети: ", err);
        }
    };


    return (
        <div className="modal-overlay">
            <div className="modal">
                <h2 className="modal-title">Создать задачу</h2>
                <form onSubmit={handleSubmit} className="form">
                    <div className="form-group">
                        <label>Название задачи:</label>
                        <input
                            type="text"
                            value={title}
                            placeholder="Введите название"
                            onChange={(e) => setTitle(e.target.value)}
                            className="input-field"
                        />
                    </div>
                    <div className="form-group">
                        <label>Описание задачи:</label>
                        <ReactQuill
                            theme="snow"
                            value={description}
                            onChange={setDescription}
                            className="rich-editor"
                        />
                    </div>
                    <div className="form-group">
                        <label>Крайний срок:</label>
                        <input
                            type="datetime-local"
                            value={deadline}
                            onChange={(e) => setDeadline(e.target.value)}
                            className="input-field"
                        />
                    </div>
                    <div className="button-container">
                        <button type="submit" className="button-submit">
                            Сохранить
                        </button>
                        <button
                            type="button"
                            className="button-cancel"
                            onClick={onClose}
                        >
                            Отмена
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TaskForm;
