import React, { useState } from "react";
import "../create_task_form/Create_task.css";

const EditTaskModal = ({ task, onClose, onSave, setTasks }) => {
    const [title, setTitle] = useState(task.title);
    const [description, setDescription] = useState(task.description.replace(/<\/?[^>]+(>|$)/g, ""));
    const [deadline, setDeadline] = useState(task.deadline);
    const API_URL = process.env.REACT_APP_API_URL;

    const handleSave = async (e) => {
        e.preventDefault();

        if (!setTasks || typeof setTasks !== "function") {
            console.error("Ошибка: setTasks не является функцией!");
            return;
        }

        const token = localStorage.getItem("token");
        if (!token) {
            console.error("Ошибка: Токен отсутствует.");
            return;
        }

        const formattedDeadline = deadline ? new Date(deadline).toISOString() : null;

        const updatedTask = {
            title,
            description: description.replace(/<\/?[^>]+(>|$)/g, ""),
            deadline: formattedDeadline,
            status: task.status,
        };

        try {
            const response = await fetch(`${API_URL}/tasks/${task.id}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`,
                },
                body: JSON.stringify(updatedTask),
            });

            if (!response.ok) {
                throw new Error(`Ошибка обновления: ${response.status}`);
            }

            setTasks((prev) =>
                prev.map((t) => (t.id === task.id ? { ...t, ...updatedTask } : t))
            );

            onClose();
        } catch (error) {
            console.error("Ошибка при обновлении задачи:", error);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal">
                <h2>Редактировать задачу</h2>
                <form onSubmit={handleSave}>
                    <label>Название задачи:</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />
                    <label>Описание задачи:</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        required
                    />
                    <label>Крайний срок:</label>
                    <input
                        type="datetime-local"
                        value={deadline}
                        onChange={(e) => setDeadline(e.target.value)}
                        required
                    />
                    <div className="button-container">
                        <button type="submit" className="submit-btn">Сохранить</button>
                        <button type="button" className="cancel-btn" onClick={onClose}>Отмена</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditTaskModal;
