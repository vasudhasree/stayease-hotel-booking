export const money=n=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(n||0)
export const dateText=d=>d?new Date(d).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}):'—'
export const errorText=e=>e?.response?.data?.detail||e?.message||'Something went wrong'
export const todayISO=()=>new Date().toISOString().slice(0,10)
