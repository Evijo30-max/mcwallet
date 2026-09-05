import { useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle,
  FileText,
  Loader2,
  Upload,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { getWallets } from "../../services/wallets";
import { createDeposit } from "../../services/deposits";

function Deposit() {
  const navigate = useNavigate();

  const [wallets, setWallets] = useState([]);

  const [loadingWallets, setLoadingWallets] = useState(true);
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

  const [step, setStep] = useState(1);

  const [currency, setCurrency] = useState("XAF");
  const [montant, setMontant] = useState("");
  const [methode, setMethode] = useState("Orange Money");

  const [referencePaiement, setReferencePaiement] =
    useState("");

  const [nomDeposant, setNomDeposant] =
    useState("");

  const [justificatif, setJustificatif] =
    useState(null);

  useEffect(() => {
    loadWallets();
  }, []);

  async function loadWallets() {
    try {
      setLoadingWallets(true);
      setError("");

      const data = await getWallets();

      setWallets(data);

      if (data.length > 0) {
        setCurrency(data[0].currency);
      }
    } catch (err) {
      console.error(err);
      setError(
        "Impossible de récupérer vos comptes."
      );
    } finally {
      setLoadingWallets(false);
    }
  }

  const selectedWallet = wallets.find(
    (wallet) => wallet.currency === currency
  );

  function validateStepOne() {
    if (!selectedWallet) {
      setError(
        "Le compte sélectionné est indisponible."
      );
      return false;
    }

    if (!methode) {
      setError(
        "Veuillez choisir une méthode de paiement."
      );
      return false;
    }

    return true;
  }

  function validateStepTwo() {
    if (!montant || Number(montant) <= 0) {
      setError(
        "Veuillez saisir un montant valide."
      );
      return false;
    }

    if (!referencePaiement.trim()) {
      setError(
        "Veuillez saisir la référence du paiement."
      );
      return false;
    }

    return true;
  }

  function nextStep() {
    setError("");

    if (step === 1 && !validateStepOne()) {
      return;
    }

    if (step === 2 && !validateStepTwo()) {
      return;
    }

    setStep((current) => current + 1);
  }

  function previousStep() {
    setError("");
    setStep((current) => Math.max(1, current - 1));
  }

  async function handleSubmit() {
    try {
      setLoading(true);
      setError("");

      const response = await createDeposit({
        montant,
        currency,
        methode,
        reference_paiement:
          referencePaiement,
        nom_deposant:
          nomDeposant,
        justificatif,
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

  if (loadingWallets) {
    return (
      <main className="deposit-page">
        <section className="deposit-card">
          <div className="deposit-loading">
            <Loader2
              size={20}
              className="spin"
            />
            Chargement de vos comptes...
          </div>
        </section>
      </main>
    );
  }

  if (success) {
    return (
      <main className="deposit-page">
        <section className="deposit-card success-card">

          <div className="success-icon">
            <CheckCircle size={52} />
          </div>

          <h1>Demande envoyée</h1>

          <p>
            Votre demande de dépôt a été
            enregistrée avec succès.
          </p>

          <div className="deposit-summary">

            <div>
              <span>Montant</span>

              <strong>
                {Number(
                  success.montant
                ).toLocaleString("fr-FR")}{" "}
                {success.currency}
              </strong>
            </div>

            <div>
              <span>Méthode</span>

              <strong>
                {success.methode}
              </strong>
            </div>

            <div>
              <span>Référence MCWallet</span>

              <strong>
                {success.reference}
              </strong>
            </div>

            <div>
              <span>Statut</span>

              <strong>
                En attente de validation
              </strong>
            </div>

          </div>

          <div className="success-info">
            <p>
              Votre solde n'est pas encore crédité.
              Un administrateur doit vérifier votre
              dépôt avant validation.
            </p>
          </div>

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
          <h1>
            Déposer de l'argent
          </h1>

          <p>
            Effectuez votre dépôt en quelques étapes.
          </p>
        </div>

        <div className="deposit-steps">
          <span className={step >= 1 ? "active" : ""}>
            1
          </span>

          <span className={step >= 2 ? "active" : ""}>
            2
          </span>

          <span className={step >= 3 ? "active" : ""}>
            3
          </span>
        </div>

        {error && (
          <div className="deposit-error">
            {error}
          </div>
        )}

        {step === 1 && (
          <section>

            <h2>1. Choisir le compte</h2>

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

            <div className="form-group">

              <label htmlFor="methode">
                Moyen de paiement
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

            <div className="payment-instructions">
              <h3>
                Instructions
              </h3>

              <p>
                Effectuez d'abord votre paiement
                avec la méthode sélectionnée.
              </p>

              <p>
                Conservez votre reçu ou votre
                référence de paiement.
              </p>
            </div>

            <button
              type="button"
              className="deposit-button"
              onClick={nextStep}
            >
              Continuer
            </button>

          </section>
        )}

        {step === 2 && (
          <section>

            <h2>2. Informations du dépôt</h2>

            <div className="form-group">

              <label htmlFor="montant">
                Montant
              </label>

              <input
                id="montant"
                type="number"
                min="0.01"
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
              />

              <small>
                Devise : {currency}
              </small>

            </div>

            <div className="form-group">

              <label htmlFor="referencePaiement">
                Référence du paiement
              </label>

              <input
                id="referencePaiement"
                type="text"
                value={referencePaiement}
                onChange={(event) =>
                  setReferencePaiement(
                    event.target.value
                  )
                }
                placeholder="Exemple : OM123456789"
              />

            </div>

            <div className="form-group">

              <label htmlFor="nomDeposant">
                Nom du déposant
              </label>

              <input
                id="nomDeposant"
                type="text"
                value={nomDeposant}
                onChange={(event) =>
                  setNomDeposant(
                    event.target.value
                  )
                }
                placeholder="Nom utilisé lors du paiement"
              />

            </div>

            <div className="deposit-actions">

              <button
                type="button"
                className="back-button"
                onClick={previousStep}
              >
                Retour
              </button>

              <button
                type="button"
                className="deposit-button"
                onClick={nextStep}
              >
                Continuer
              </button>

            </div>

          </section>
        )}

        {step === 3 && (
          <section>

            <h2>3. Justificatif</h2>

            <p>
              Ajoutez le reçu ou justificatif
              correspondant à votre paiement.
            </p>

            <label
              htmlFor="justificatif"
              className="file-upload"
            >
              <Upload size={24} />

              <span>
                {justificatif
                  ? justificatif.name
                  : "Choisir un justificatif"}
              </span>

              <input
                id="justificatif"
                type="file"
                accept="image/*,.pdf"
                onChange={(event) =>
                  setJustificatif(
                    event.target.files?.[0] ||
                    null
                  )
                }
              />
            </label>

            <div className="deposit-summary">

              <div>
                <span>Compte</span>
                <strong>{currency}</strong>
              </div>

              <div>
                <span>Montant</span>
                <strong>
                  {Number(
                    montant || 0
                  ).toLocaleString("fr-FR")}{" "}
                  {currency}
                </strong>
              </div>

              <div>
                <span>Méthode</span>
                <strong>{methode}</strong>
              </div>

              <div>
                <span>Référence paiement</span>
                <strong>
                  {referencePaiement}
                </strong>
              </div>

            </div>

            <div className="deposit-actions">

              <button
                type="button"
                className="back-button"
                onClick={previousStep}
              >
                Retour
              </button>

              <button
                type="button"
                className="deposit-button"
                disabled={loading}
                onClick={handleSubmit}
              >
                {loading ? (
                  <>
                    <Loader2
                      size={18}
                      className="spin"
                    />
                    Envoi...
                  </>
                ) : (
                  <>
                    <FileText size={18} />
                    Envoyer la demande
                  </>
                )}
              </button>

            </div>

          </section>
        )}

      </section>
    </main>
  );
}

export default Deposit;