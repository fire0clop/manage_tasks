import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TaskForm from './components/create_task_form/Create_task';
import TaskList from './components/task_list/List_tasks';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<TaskList />} />
                <Route path="/tasks/new" element={<TaskForm />} />
            </Routes>
        </Router>
    );
}

export default App;