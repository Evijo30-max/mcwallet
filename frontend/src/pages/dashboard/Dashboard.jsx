
import {
  ArrowDownToLine,
  ArrowUpFromLine,
  ArrowLeftRight,
  Wallet,
  TrendingUp,
} from "lucide-react";

function Dashboard() {
  const currencies = [
    {
      code: "XAF",
      name: "Franc CFA",
      balance: "0",
      symbol: "FCFA",
    },
    {
      code: "USD",
      name: "Dollar américain",
      balance: "0",
      symbol: "$",
    },
    {
      code: "EUR",
      name: "Euro",
      balance: "0",
      symbol: "€",
    },
  ];

  return (
    <div className="dashboard">
      {/* =====================================================
          EN-TÊTE DU DASHBOARD
          ===================================================== */}

      <div className="dashboard-heading">
        <div>
          <h1>Vue d'ensemble</h1>
          <p>
            Retrouvez ici l'état de vos comptes et vos dernières opérations.
          </p>
        </div>
      </div>

      {/* =====================================================
          SOLDE TOTAL
          ===================================================== */}

      <section className="total-balance-card">
        <div className="total-balance-content">
          <div className="total-balance-icon">
            <Wallet size={24} />
          </div>

          <div>
            <p>Valeur totale du portefeuille</p>

            <h2>0 FCFA</h2>

            <span>
              Équivalent approximatif de vos avoirs dans toutes les devises
            </span>
          </div>
        </div>

        <div className="balance-trend">
          <TrendingUp size={17} />
          <span>Portefeuille</span>
        </div>
      </section>

      {/* =====================================================
          ACTIONS RAPIDES
          ===================================================== */}

      <section className="quick-actions-section">
        <h2>Actions rapides</h2>

        <div className="quick-actions">
          <button
            className="quick-action deposit"
            onClick={() => {
              window.location.href = "/deposit";
            }}
          >
            <span className="quick-action-icon">
              <ArrowDownToLine size={21} />
            </span>

            <span>
              <strong>Déposer</strong>
              <small>Ajouter de l'argent</small>
            </span>
          </button>

          <button
            className="quick-action withdraw"
            onClick={() => {
              window.location.href = "/withdraw";
            }}
          >
            <span className="quick-action-icon">
              <ArrowUpFromLine size={21} />
            </span>

            <span>
              <strong>Retirer</strong>
              <small>Retirer de l'argent</small>
            </span>
          </button>

          <button
            className="quick-action convert"
            onClick={() => {
              window.location.href = "/convert";
            }}
          >
            <span className="quick-action-icon">
              <ArrowLeftRight size={21} />
            </span>

            <span>
              <strong>Convertir</strong>
              <small>Changer de devise</small>
            </span>
          </button>
        </div>
      </section>

      {/* =====================================================
          COMPTES
          ===================================================== */}

      <section className="accounts-section">
        <div className="section-header">
          <div>
            <h2>Mes comptes</h2>
            <p>Vos soldes par devise.</p>
          </div>

          <a href="/accounts">Voir tous les comptes</a>
        </div>

        <div className="currency-grid">
          {currencies.map((currency) => (
            <div className="currency-card" key={currency.code}>
              <div className="currency-card-top">
                <div className="currency-code">
                  {currency.code}
                </div>

                <span>{currency.name}</span>
              </div>

              <div className="currency-balance">
                <span>{currency.symbol}</span>
                <strong>{currency.balance}</strong>
              </div>

              <div className="currency-card-footer">
                <span>Solde disponible</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* =====================================================
          TRANSACTIONS RÉCENTES
          ===================================================== */}

      <section className="transactions-section">
        <div className="section-header">
          <div>
            <h2>Transactions récentes</h2>
            <p>Les dernières opérations effectuées sur vos comptes.</p>
          </div>

          <a href="/transactions">Voir tout</a>
        </div>

        <div className="empty-transactions">
          <div className="empty-transactions-icon">
            <ArrowLeftRight size={22} />
          </div>

          <h3>Aucune transaction</h3>

          <p>
            Vos opérations financières apparaîtront ici.
          </p>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
