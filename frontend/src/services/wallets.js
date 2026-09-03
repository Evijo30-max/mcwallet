import api from "./api";

export async function getWallets() {
  const response = await api.get("/wallets/");
  return response.data.wallets;
}

export async function getWallet(currency) {
  const response = await api.get(`/wallets/${currency}/`);
  return response.data.wallet;
}