import React, { useEffect, useState } from "react";
import TaskForm from "../create_task_form/Create_task";
import "./List_tasks.css";
import EditTaskModal from "./Edit_task";

const TaskList = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [expandedTask, setExpandedTask] = useState(null);
    const [taskToEdit, setTaskToEdit] = useState(null);
    const [searchTerm, setSearchTerm] = useState("");

    const [limits, setLimits] = useState({
        new: 5,
        in_progress: 5,
        completed: 5,
    });
    const handleSearchChange = (event) => {
        setSearchTerm(event.target.value);
    };

    const [sortOrder, setSortOrder] = useState("asc");
    const getTasksWithLimit = (status) => {
        return tasks
            .filter((task) =>
                (task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    task.description.toLowerCase().includes(searchTerm.toLowerCase())) &&
                task.status === status
            )
            .slice(0, limits[status]);
    };


    const sortTasksByDeadline = () => {
        setTasks((prevTasks) =>
            [...prevTasks].sort((a, b) => {
                const dateA = new Date(a.deadline);
                const dateB = new Date(b.deadline);
                return sortOrder === "asc" ? dateA - dateB : dateB - dateA;
            })
        );
        setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    };

    const normalizeStatus = (status) => {
        switch (status) {
            case "новая":
                return "new";
            case "в процессе":
                return "in_progress";
            case "завершена":
                return "completed";
            default:
                return status;
        }
    };
    const handleDeleteTask = async (taskId) => {
        if (!taskId) {
            console.error("Ошибка: ID задачи не указан");
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/tasks/${taskId}`, {
                method: "DELETE",
            });

            if (!response.ok) {
                throw new Error(`Ошибка удаления задачи: ${response.status}`);
            }

            console.log(`Задача с ID ${taskId} успешно удалена`);

            // Обновляем состояние, удаляя задачу из списка
            setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
        } catch (error) {
            console.error("Ошибка при удалении задачи:", error);
        }
    };

    const fetchTasks = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8000/tasks");
            if (!response.ok) {
                throw new Error(`Ошибка загрузки данных: ${response.status}`);
            }
            const data = await response.json();
            console.log("Полученные задачи:", data);

            const formattedData = data.map((task) => ({
                id: task[0],
                title: task[1],
                description: task[2],
                status: normalizeStatus(task[3]),
                deadline: task[4]
            }));

            console.log("Преобразованные задачи:", formattedData);

            setTasks(formattedData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const calculateDaysLeft = (deadline) => {
        const today = new Date();
        const deadlineDate = new Date(deadline);
        const diffTime = deadlineDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays > 0) {
            return `${diffDays} дней`;
        } else if (diffDays === 0) {
            return "Сегодня";
        } else {
            return "Просрочена";
        }
    };

    const formatDate = (dateString) => {
        const options = { day: "2-digit", month: "2-digit", year: "numeric" };
        return new Date(dateString).toLocaleDateString("ru-RU", options);
    };

    const handleEditTask = (task) => setTaskToEdit(task);

    const handleUpdateTask = async (updatedTask) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/tasks/${updatedTask.id}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(updatedTask),
            });

            if (!response.ok) {
                throw new Error(`Ошибка обновления задачи: ${response.status}`);
            }

            setTasks((prev) =>
                prev.map((task) => (task.id === updatedTask.id ? { ...task, ...updatedTask } : task))
            );

            setTaskToEdit(null);
        } catch (err) {
            console.error("Ошибка обновления задачи:", err.message);
        }
    };

    const toggleExpansion = (id) => {
        setExpandedTask((prev) => (prev === id ? null : id));
    };

    const handleLoadMore = () => {
        setLimits((prevLimits) => ({
            new: prevLimits.new + 5,
            in_progress: prevLimits.in_progress + 5,
            completed: prevLimits.completed + 5,
        }));
    };

    const translateStatus = (status) => {
        switch (status) {
            case "new":
                return "новая";
            case "in_progress":
                return "в процессе";
            case "completed":
                return "завершена";
            default:
                return status;
        }
    };

    const handleChangeStatus = async (taskId, newStatus) => {
        const translatedStatus = translateStatus(newStatus);

        if (!taskId) {
            console.error("Ошибка: ID задачи не указан");
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/tasks/${taskId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ status: translatedStatus }),
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            console.log(`Успешно обновили статус задачи ID ${taskId} на "${translatedStatus}"`);

            await fetchTasks();
        } catch (error) {
            console.error("Ошибка при изменении статуса задачи:", error);
        }
    };

    const handleDragStart = (event, taskId) => {
        event.dataTransfer.setData("taskId", String(taskId));
    };

    const handleDrop = async (event, newStatus) => {
        event.preventDefault();
        const taskId = event.dataTransfer.getData("taskId");

        if (!taskId) return;

        console.log(`Перетаскивание задачи ID ${taskId} в статус ${newStatus}`);

        setTasks((prevTasks) =>
            prevTasks.map((task) =>
                task.id === parseInt(taskId) ? { ...task, status: newStatus } : task
            )
        );

        await handleChangeStatus(taskId, newStatus);
    };

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    useEffect(() => {
        fetchTasks();
    }, []);

    if (loading) {
        return <p>Загрузка задач...</p>;
    }

    if (error) {
        return <p>Ошибка загрузки задач: {error}</p>;
    }

    return (
        <div>
            <h1 className="kanban-title">Kanban-доска</h1>
            <button className="open-modal-btn" onClick={sortTasksByDeadline}>
                Сортировать по дедлайну ({sortOrder === "asc" ? "↑" : "↓"})
            </button>

            <button className="open-modal-btn" onClick={() => setIsModalOpen(true)}>
                Создать задачу
            </button>
            <input
                type="text"
                placeholder="Поиск задач..."
                value={searchTerm}
                onChange={handleSearchChange}
                className="search-input"
            />

            <div className="kanban-container">
                {["new", "in_progress", "completed"].map((status) => (
                    <div
                        key={status}
                        className="kanban-column"
                        onDrop={(event) => handleDrop(event, status)} // Обрабатываем сброс
                        onDragOver={handleDragOver} // Разрешаем сброс
                    >
                        <h2 className="kanban-column-title">
                            {status === "new"
                                ? "Новые"
                                : status === "in_progress"
                                    ? "В процессе"
                                    : "Завершенные"}
                        </h2>
                        <ul className="kanban-task-list">
                            {getTasksWithLimit(status).map((task) => (
                                <li
                                    key={task.id}
                                    className="task-card"
                                    draggable // Активируем возможность перетаскивания
                                    onDragStart={(event) => handleDragStart(event, task.id)}
                                >
                                    <div className="task-header">
                                        <div className="left-section">
                                            {/* Название */}
                                            <span className="task-title">{task.title}</span>
                                            {/* Дата дедлайна */}
                                            <div className="task-deadline">
                                                <span>{formatDate(task.deadline)}</span>
                                                <span> ({calculateDaysLeft(task.deadline)})</span>
                                            </div>
                                        </div>

                                        {/* Кнопка разворачивания (остается в верхнем правом углу) */}
                                        <button
                                            className="toggle-description-btn"
                                            onClick={() => toggleExpansion(task.id)}
                                        >
                                            {expandedTask === task.id ? "▲" : "▼"}
                                        </button>
                                    </div>

                                    {/* Описание задачи */}
                                    <div className="task-body">
                                        <div
                                            dangerouslySetInnerHTML={{
                                                __html:
                                                    expandedTask === task.id
                                                        ? task.description
                                                        : `${task.description.replace(/<\/?[^>]+(>|$)/g, "").substr(0, 50)}...`,
                                            }}
                                        ></div>

                                        {/* Кнопки редактирования и удаления внизу справа */}
                                        <div className="button-group">
                                            <button className="edit-task-btn" onClick={() => handleEditTask(task)}>
                                                ✏️
                                            </button>
                                            <button className="delete-task-btn" onClick={() => handleDeleteTask(task.id)}>
                                                ❌
                                            </button>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                        {tasks.filter((task) => task.status === status).length >
                            limits[status] && (
                                <button className="load-more-btn" onClick={handleLoadMore}>
                                    Загрузить ещё
                                </button>
                            )}
                    </div>
                ))}
            </div>

            {isModalOpen && (
                <div className="modal-overlay">
                    <TaskForm onClose={() => setIsModalOpen(false)} onTaskCreated={fetchTasks} />
                </div>
            )}

            {taskToEdit && (
                <div className="modal-overlay">
                    <EditTaskModal
                        task={taskToEdit}
                        onClose={() => setTaskToEdit(null)}
                        onSave={handleUpdateTask}
                    />
                </div>
            )}
        </div>
    );
};

export default TaskList;