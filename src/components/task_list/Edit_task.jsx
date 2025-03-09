import React, { useState } from "react";
import "../create_task_form/Create_task.css"; // Используем стили окна создания задачи

const EditTaskModal = ({ task, onClose, onSave }) => {
    const [title, setTitle] = useState(task.title);
    const [description, setDescription] = useState(task.description.replace(/<\/?[^>]+(>|$)/g, ""));
    const [deadline, setDeadline] = useState(task.deadline);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave({ ...task, title, description, deadline });
    };

    return (
        <div className="modal-overlay">
            <div className="modal">
                <h2>Редактировать задачу</h2>
                <form onSubmit={handleSubmit}>
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
                        <button type="submit" className="submit-btn">
                            Сохранить
                        </button>
                        <button type="button" className="cancel-btn" onClick={onClose}>
                            Отмена
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditTaskModal;