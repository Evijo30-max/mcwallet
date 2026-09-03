import api from "./api";

/**
 * Crée une nouvelle demande de dépôt.
 *
 * La demande reste en attente jusqu'à sa validation
 * par l'administration.
 */
export async function createDeposit({
  walletId,
  montant,
  currency,
  methode,
}) {
  const response = await api.post("/deposits/", {
    wallet: walletId,
    montant,
    currency,
    methode,
  });

  return response.data;
}

/**
 * Récupère les demandes de dépôt de l'utilisateur connecté.
 */
export async function getDeposits() {
  const response = await api.get("/deposits/");
  return response.data.deposits;
}