import { useEffect, useState } from "react";
import {
  ArrowDownToLine,
  ArrowLeftRight,
  ArrowUpFromLine,
  Eye,
  EyeOff,
  LogOut,
  Wallet,
} from "lucide-react";


import { useAuth } from "../../context/AuthContext";
import { getWallets } from "../../services/wallets";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [wallets, setWallets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showBalances, setShowBalances] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadWallets();
  }, []);

  async function loadWallets() {
    try {
      setLoading(true);
      setError("");

      const data = await getWallets();
      setWallets(data);
    } catch (err) {
      console.error(err);
      setError("Impossible de récupérer vos comptes.");
    } finally {
      setLoading(false);
    }
  }

  const walletByCurrency = (currency) =>
    wallets.find((wallet) => wallet.currency === currency);

  const xaf = walletByCurrency("XAF");
  const usd = walletByCurrency("USD");
  const eur = walletByCurrency("EUR");

  return (
    <div className="dashboard-page">

      {/* HEADER */}
      <header className="dashboard-header">
        <div>
          <div className="dashboard-brand">
            <Wallet size={26} />
            <span>MCWallet</span>
          </div>

          <p className="dashboard-subtitle">
            Votre portefeuille multi-devises
          </p>
        </div>

        <div className="dashboard-header-actions">
          <button
            className="icon-button"
            onClick={() => setShowBalances(!showBalances)}
            title={
              showBalances
                ? "Masquer les soldes"
                : "Afficher les soldes"
            }
          >
            {showBalances ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>

          <button className="logout-button" onClick={logout}>
            <LogOut size={18} />
            Déconnexion
          </button>
        </div>
      </header>

      {/* CONTENU */}
      <main className="dashboard-content">

        {/* BIENVENUE */}
        <section className="welcome-section">
          <p className="welcome-label">Bonjour</p>

          <h1>
            {user?.prenom} {user?.nom}
          </h1>

          <p>
            Voici un aperçu de vos comptes MCWallet.
          </p>
        </section>

        {/* SOLDE TOTAL */}
        <section className="total-balance-card">
          <div>
            <span>Votre portefeuille</span>

            <h2>
              {showBalances
                ? "Multi-devises"
                : "••••••••"}
            </h2>

            <p>
              Vos comptes sont séparés par devise.
            </p>
          </div>

          <Wallet size={42} />
        </section>

        {/* COMPTES */}
        <section className="wallet-section">

          <div className="section-heading">
            <div>
              <h2>Mes comptes</h2>
              <p>Vos soldes disponibles</p>
            </div>
          </div>

          {loading && (
            <div className="dashboard-message">
              Chargement de vos comptes...
            </div>
          )}

          {error && (
            <div className="dashboard-error">
              {error}
            </div>
          )}

          {!loading && !error && (
            <div className="wallet-grid">

              <WalletCard
                wallet={xaf}
                flag="🇨🇲"
                name="Franc CFA"
                showBalance={showBalances}
              />

              <WalletCard
                wallet={usd}
                flag="🇺🇸"
                name="Dollar américain"
                showBalance={showBalances}
              />

              <WalletCard
                wallet={eur}
                flag="🇪🇺"
                name="Euro"
                showBalance={showBalances}
              />

            </div>
          )}
        </section>

        {/* ACTIONS */}
        <section className="actions-section">

          <div className="section-heading">
            <div>
              <h2>Actions rapides</h2>
              <p>Gérez facilement votre argent</p>
            </div>
          </div>

          <div className="action-grid">

            <button
              className="action-card"
              onClick={() => navigate("/deposit")}
            >
              <span className="action-icon">
                <ArrowDownToLine size={22} />
              </span>

              <span>
                <strong>Déposer</strong>
                <small>Ajouter de l'argent</small>
              </span>
            </button>

            <button className="action-card">
              <span className="action-icon">
                <ArrowUpFromLine size={22} />
              </span>

              <span>
                <strong>Retirer</strong>
                <small>Retirer de l'argent</small>
              </span>
            </button>

            <button className="action-card">
              <span className="action-icon">
                <ArrowLeftRight size={22} />
              </span>

              <span>
                <strong>Convertir</strong>
                <small>Changer de devise</small>
              </span>
            </button>

          </div>
        </section>

      </main>
    </div>
  );
}

function WalletCard({
  wallet,
  flag,
  name,
  showBalance,
}) {
  if (!wallet) {
    return (
      <article className="wallet-card wallet-disabled">
        <div className="wallet-card-top">
          <span className="wallet-flag">{flag}</span>

          <span className="wallet-currency">
            Compte
          </span>
        </div>

        <h3>{name}</h3>

        <p>Compte indisponible</p>
      </article>
    );
  }

  return (
    <article className="wallet-card">

      <div className="wallet-card-top">
        <span className="wallet-flag">{flag}</span>

        <span className="wallet-currency">
          {wallet.currency}
        </span>
      </div>

      <h3>{name}</h3>

      <div className="wallet-balance">
        {showBalance
          ? formatBalance(wallet.balance, wallet.currency)
          : "••••••"}
      </div>

      <span className="wallet-status">
        {wallet.actif ? "Compte actif" : "Compte désactivé"}
      </span>

    </article>
  );
}

function formatBalance(balance, currency) {
  const number = Number(balance);

  if (currency === "XAF") {
    return `${number.toLocaleString("fr-FR")} FCFA`;
  }

  if (currency === "USD") {
    return `$${number.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }

  if (currency === "EUR") {
    return `${number.toLocaleString("fr-FR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} €`;
  }

  return `${balance} ${currency}`;
}

export default Dashboard;