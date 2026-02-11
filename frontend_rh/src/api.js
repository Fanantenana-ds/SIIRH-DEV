// import axios from "axios";

// const API_URL = "http://localhost:8000";

// export const api = axios.create({
//   baseURL: API_URL,
// });




import axios from "axios";


export const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api";


const api = axios.create({
baseURL: API_BASE,
headers: { "Content-Type": "application/json" },
});


export default api;