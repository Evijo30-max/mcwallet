import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle, Loader2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { getWallets } from "../../services/wallets";
import { createDeposit } from "../../services/deposits";

function Deposit() {
  const navigate = useNavigate();

  const [wallets, setWallets] = useState([]);
  const [loadingWallets, setLoadingWallets] = useState(true);

  const [currency, setCurrency] = useState("XAF");
  const [montant, setMontant] = useState("");
  const [methode, setMethode] = useState("Orange Money");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadWallets();
  }, []);

  async function loadWallets() {
    try {
      setLoadingWallets(true);
      setError("");

      const data = await getWallets();
      setWallets(data);
    } catch (err) {
      console.error(err);
      setError("Impossible de récupérer vos comptes.");
    } finally {
      setLoadingWallets(false);
    }
  }

  const selectedWallet = wallets.find(
    (wallet) => wallet.currency === currency
  );

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");

    if (!selectedWallet) {
      setError("Le compte sélectionné est indisponible.");
      return;
    }

    if (!montant || Number(montant) <= 0) {
      setError("Veuillez saisir un montant valide.");
      return;
    }

    try {
      setLoading(true);

      const response = await createDeposit({
        walletId: selectedWallet.id,
        montant: montant,
        currency: currency,
        methode: methode,
      });

      setSuccess(response.deposit);
    } catch (err) {
      console.error(err);

      const message =
        err.response?.data?.message ||
        err.response?.data?.detail ||
        "Impossible de créer la demande de dépôt.";

      setError(message);
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <main className="deposit-page">
        <section className="deposit-card success-card">
          <div className="success-icon">
            <CheckCircle size={48} />
          </div>

          <h1>Demande envoyée</h1>

          <p>
            Votre demande de dépôt a bien été enregistrée.
          </p>

          <div className="deposit-summary">
            <div>
              <span>Montant</span>
              <strong>
                {Number(success.montant).toLocaleString("fr-FR")}{" "}
                {success.currency}
              </strong>
            </div>

            <div>
              <span>Méthode</span>
              <strong>{success.methode}</strong>
            </div>

            <div>
              <span>Référence</span>
              <strong>{success.reference}</strong>
            </div>

            <div>
              <span>Statut</span>
              <strong>En attente de validation</strong>
            </div>
          </div>

          <p className="success-info">
            Votre solde ne sera crédité qu'après validation de votre
            dépôt par MCWallet.
          </p>

          <button
            className="deposit-button"
            onClick={() => navigate("/")}
          >
            Retour au tableau de bord
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="deposit-page">
      <section className="deposit-card">

        <button
          type="button"
          className="back-button"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Retour
        </button>

        <div className="deposit-header">
          <h1>Déposer de l'argent</h1>

          <p>
            Choisissez le compte à créditer et indiquez le montant
            que vous souhaitez déposer.
          </p>
        </div>

        {loadingWallets && (
          <div className="deposit-loading">
            <Loader2 size={20} className="spin" />
            Chargement de vos comptes...
          </div>
        )}

        {!loadingWallets && (
          <form onSubmit={handleSubmit}>

            <div className="form-group">
              <label htmlFor="currency">
                Compte à créditer
              </label>

              <select
                id="currency"
                value={currency}
                onChange={(event) =>
                  setCurrency(event.target.value)
                }
              >
                {wallets.map((wallet) => (
                  <option
                    key={wallet.id}
                    value={wallet.currency}
                  >
                    {wallet.currency}
                  </option>
                ))}
              </select>
            </div>

            <div className="selected-account">
              <span>Compte sélectionné</span>

              <strong>
                {currency === "XAF" && "🇨🇲 Franc CFA"}
                {currency === "USD" && "🇺🇸 Dollar américain"}
                {currency === "EUR" && "🇪🇺 Euro"}
              </strong>
            </div>

            <div className="form-group">
              <label htmlFor="montant">
                Montant du dépôt
              </label>

              <input
                id="montant"
                type="number"
                min="1"
                step="0.01"
                value={montant}
                onChange={(event) =>
                  setMontant(event.target.value)
                }
                placeholder={
                  currency === "XAF"
                    ? "Exemple : 50000"
                    : "Exemple : 100"
                }
                required
              />

              <small>
                Devise : {currency}
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="methode">
                Méthode de paiement
              </label>

              <select
                id="methode"
                value={methode}
                onChange={(event) =>
                  setMethode(event.target.value)
                }
              >
                <option value="Orange Money">
                  Orange Money
                </option>

                <option value="MTN Mobile Money">
                  MTN Mobile Money
                </option>

                <option value="Dépôt bancaire">
                  Dépôt bancaire
                </option>
              </select>
            </div>

            {error && (
              <div className="deposit-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="deposit-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="spin" />
                  Envoi en cours...
                </>
              ) : (
                "Continuer"
              )}
            </button>
          </form>
        )}
      </section>
    </main>
  );
}

export default Deposit;