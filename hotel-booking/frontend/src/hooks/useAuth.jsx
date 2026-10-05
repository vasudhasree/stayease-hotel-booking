import {createContext,useContext,useEffect,useState} from 'react'
import {api} from '../api/client'
const AuthContext=createContext(null)
export function AuthProvider({children}){
 const [user,setUser]=useState(()=>{try{return JSON.parse(sessionStorage.getItem('stayease_user'))}catch{return null}})
 const login=async(email,password)=>{const {data}=await api.post('/api/auth/login',{email,password});sessionStorage.setItem('stayease_token',data.access_token);sessionStorage.setItem('stayease_user',JSON.stringify(data.user));setUser(data.user);return data.user}
 const register=async(payload)=>{const {data}=await api.post('/api/auth/register',payload);sessionStorage.setItem('stayease_token',data.access_token);sessionStorage.setItem('stayease_user',JSON.stringify(data.user));setUser(data.user);return data.user}
 const logout=()=>{sessionStorage.removeItem('stayease_token');sessionStorage.removeItem('stayease_user');setUser(null);location.href='/login'}
 useEffect(()=>{if(!user)return; api.get('/api/users/me').then(r=>{setUser(r.data);sessionStorage.setItem('stayease_user',JSON.stringify(r.data))}).catch(()=>{})},[])
 return <AuthContext.Provider value={{user,login,register,logout}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext)
