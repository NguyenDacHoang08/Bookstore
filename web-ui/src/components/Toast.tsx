import type { Toast as ToastType } from '../types'

type ToastProps = {
  toast: ToastType | null
}

export default function Toast({ toast }: ToastProps) {
  if (!toast) return null
  return (
    <div className={`toast ${toast.type}`}>
      <span>{toast.message}</span>
    </div>
  )
}
