// import axios from "axios";

// const API_URL = "http://127.0.0.1:8000/api/paies/";

// export const getPaies = () => axios.get(API_URL);

// export const createPaie = (data) => axios.post(API_URL, data);

// export const updatePaie = (id, data) =>
//   axios.put(`${API_URL}${id}`, data);

// export const deletePaie = (id) =>
//   axios.delete(`${API_URL}${id}`);











import axios from "axios";

// ✅ URL mifanaraka amin'ny backend FastAPI
const API_URL = "http://127.0.0.1:8000/api/paies/";

// Get toutes les paies
export const getPaies = () => axios.get(API_URL);

// Créer une paie (payload minimal)
export const createPaie = (data) => axios.post(API_URL, data);

// Mettre à jour une paie
export const updatePaie = (id, data) =>
  axios.put(`${API_URL}${id}`, data);

// Supprimer une paie
export const deletePaie = (id) =>
  axios.delete(`${API_URL}${id}`);
