import axios from 'axios'
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const api = axios.create({baseURL:API_URL,headers:{'Content-Type':'application/json'}})
api.interceptors.request.use(config=>{const token=sessionStorage.getItem('stayease_token');if(token)config.headers.Authorization=`Bearer ${token}`;return config})
api.interceptors.response.use(r=>r,err=>{if(err.response?.status===401){sessionStorage.removeItem('stayease_token');sessionStorage.removeItem('stayease_user');if(location.pathname!=='/login')location.href='/login'}return Promise.reject(err)})
