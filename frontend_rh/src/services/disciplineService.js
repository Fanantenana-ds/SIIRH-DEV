import axios from "axios";

const API_URL = "http://127.0.0.1:8000/discipline";

export const getCases = async () => {
  const res = await axios.get(`${API_URL}/cases`);
  return res.data;
};

export const getCase = async (id) => {
  const res = await axios.get(`${API_URL}/cases/${id}`);
  return res.data;
};

export const createCase = async (data) => {
  const res = await axios.post(`${API_URL}/cases`, data);
  return res.data;
};

export const createConvocation = async (id, data) => {
  const res = await axios.post(`${API_URL}/cases/${id}/convocation`, data);
  return res.data.pdf_url;
};

export const createDecision = async (id, data) => {
  const res = await axios.post(`${API_URL}/cases/${id}/decision`, data);
  return res.data.pdf_url;
};

export const uploadEvidence = async (id, file) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${API_URL}/cases/${id}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};
