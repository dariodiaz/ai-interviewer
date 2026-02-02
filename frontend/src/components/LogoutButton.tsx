import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface LogoutButtonProps {
    className?: string;
}

export default function LogoutButton({ className = '' }: LogoutButtonProps) {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <button
            type="button"
            onClick={handleLogout}
            className={`px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm font-medium shadow-md ${className}`}
        >
            Logout
        </button>
    );
}
