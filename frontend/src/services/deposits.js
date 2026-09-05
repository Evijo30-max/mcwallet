import api from "./api";

export async function getDeposits() {
  const response = await api.get("/transactions/deposits/");
  return response.data.deposits;
}

export async function getDeposit(id) {
  const response = await api.get(`/transactions/deposits/${id}/`);
  return response.data.deposit;
}

export async function createDeposit(data) {
  const formData = new FormData();

  formData.append("montant", data.montant);
  formData.append("currency", data.currency);
  formData.append("methode", data.methode);

  if (data.reference_paiement) {
    formData.append(
      "reference_paiement",
      data.reference_paiement
    );
  }

  if (data.nom_deposant) {
    formData.append(
      "nom_deposant",
      data.nom_deposant
    );
  }

  if (data.justificatif) {
    formData.append(
      "justificatif",
      data.justificatif
    );
  }

  const response = await api.post(
    "/transactions/deposits/",
    formData
  );

  return response.data;
}