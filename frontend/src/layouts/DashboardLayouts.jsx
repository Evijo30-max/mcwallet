import React from "react";

import {
    ArrowDownToLine,
    ArrowLeftRight,
    ArrowUpFromLine,
    History,
    LayoutDashboard,
    LogOut,
    UserRound,
    Wallet,
    X,
  } from "lucide-react";
  
  import { NavLink } from "react-router-dom";
  import { useAuth } from "../context/AuthContext";
  
  function DashboardLayout({ children }) {
    const { user, logout } = useAuth();
  
    const [sidebarOpen, setSidebarOpen] = React.useState(false);
  
    const navigation = [
      {
        label: "Vue d'ensemble",
        path: "/",
        icon: LayoutDashboard,
      },
      {
        label: "Déposer",
        path: "/deposit",
        icon: ArrowDownToLine,
      },
      {
        label: "Retirer",
        path: "/withdraw",
        icon: ArrowUpFromLine,
      },
      {
        label: "Convertir",
        path: "/convert",
        icon: ArrowLeftRight,
      },
      {
        label: "Transactions",
        path: "/transactions",
        icon: History,
      },
      {
        label: "Mon profil",
        path: "/profile",
        icon: UserRound,
      },
    ];
  
    return (
      <div className="dashboard-layout">
  
        {/* OVERLAY MOBILE */}
        {sidebarOpen && (
          <div
            className="sidebar-overlay"
            onClick={() => setSidebarOpen(false)}
          />
        )}
  
        {/* SIDEBAR */}
        <aside
          className={`dashboard-sidebar ${
            sidebarOpen ? "sidebar-open" : ""
          }`}
        >
  
          {/* LOGO */}
          <div className="sidebar-logo">
            <div className="logo-icon">
              <Wallet size={22} />
            </div>
  
            <div>
              <strong>MCWallet</strong>
              <span>Multi-devises</span>
            </div>
  
            <button
              className="sidebar-close"
              onClick={() => setSidebarOpen(false)}
            >
              <X size={20} />
            </button>
          </div>
  
          {/* NAVIGATION */}
          <nav className="sidebar-navigation">
  
            <span className="navigation-title">
              MENU
            </span>
  
            {navigation.map((item) => {
              const Icon = item.icon;
  
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `sidebar-link ${
                      isActive ? "sidebar-link-active" : ""
                    }`
                  }
                >
                  <Icon size={20} />
  
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
  
          </nav>
  
          {/* BAS SIDEBAR */}
          <div className="sidebar-bottom">
  
            <div className="sidebar-user">
  
              <div className="user-avatar">
                {user?.prenom?.charAt(0)?.toUpperCase() || "U"}
              </div>
  
              <div className="user-information">
                <strong>
                  {user?.prenom} {user?.nom}
                </strong>
  
                <span>
                  {user?.role || "CLIENT"}
                </span>
              </div>
  
            </div>
  
            <button
              className="sidebar-logout"
              onClick={logout}
            >
              <LogOut size={19} />
              <span>Se déconnecter</span>
            </button>
  
          </div>
  
        </aside>
  
        {/* CONTENU PRINCIPAL */}
        <div className="dashboard-main">
  
          {/* HEADER MOBILE */}
          <header className="mobile-header">
  
            <button
              className="mobile-menu-button"
              onClick={() => setSidebarOpen(true)}
            >
              <span />
              <span />
              <span />
            </button>
  
            <div className="mobile-brand">
              <Wallet size={21} />
              <strong>MCWallet</strong>
            </div>
  
            <div className="mobile-avatar">
              {user?.prenom?.charAt(0)?.toUpperCase() || "U"}
            </div>
  
          </header>
  
          {/* PAGE */}
          <div className="dashboard-main-content">
            {children}
          </div>
  
        </div>
  
      </div>
    );
  }
  
  export default DashboardLayout;