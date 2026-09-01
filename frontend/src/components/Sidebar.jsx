
import { NavLink } from "react-router-dom";
import {
  ArrowDownToLine,
  ArrowLeftRight,
  ArrowUpFromLine,
  CreditCard,
  LayoutDashboard,
  List,
  User,
} from "lucide-react";

function Sidebar() {
  const links = [
    {
      to: "/",
      label: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      to: "/accounts",
      label: "Mes comptes",
      icon: CreditCard,
    },
    {
      to: "/transactions",
      label: "Transactions",
      icon: List,
    },
    {
      to: "/deposit",
      label: "Déposer",
      icon: ArrowDownToLine,
    },
    {
      to: "/withdraw",
      label: "Retirer",
      icon: ArrowUpFromLine,
    },
    {
      to: "/convert",
      label: "Convertir",
      icon: ArrowLeftRight,
    },
    {
      to: "/profile",
      label: "Profil",
      icon: User,
    },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-logo-mark">M</span>
        <span>MCWallet</span>
      </div>

      <nav className="sidebar-nav">
        {links.map((link) => {
          const Icon = link.icon;

          return (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={20} strokeWidth={2} />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <p>MCWallet</p>
        <span>Portefeuille multi-devises</span>
      </div>
    </aside>
  );
}

export default Sidebar;
