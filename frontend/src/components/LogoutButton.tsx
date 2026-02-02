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
            className={`px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 text-sm font-semibold shadow-lg ${className}`}
        >
            Logout
        </button>
    );
}
