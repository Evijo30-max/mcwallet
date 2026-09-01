
import { Bell, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function Header() {
  const { user, logout } = useAuth();

  const initials =
    `${user?.prenom?.charAt(0) || ""}${user?.nom?.charAt(0) || ""}`.toUpperCase();

  return (
    <header className="header">
      <div className="header-title">
        <h2>Tableau de bord</h2>
        <p>Gérez facilement votre argent</p>
      </div>

      <div className="header-actions">
        <button className="notification-button" type="button">
          <Bell size={20} />
          <span className="notification-dot" />
        </button>

        <div className="header-user">
          <div className="header-avatar">{initials || "U"}</div>

          <div className="header-user-info">
            <strong>
              {user?.prenom} {user?.nom}
            </strong>
            <span>{user?.email || user?.telephone}</span>
          </div>
        </div>

        <button
          className="logout-button"
          type="button"
          onClick={logout}
          title="Se déconnecter"
        >
          <LogOut size={19} />
        </button>
      </div>
    </header>
  );
}

export default Header;
