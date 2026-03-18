import type { Dispatch, SetStateAction } from 'react'
import type { LoginForm } from '../types'

type LoginPanelProps = {
  loginForm: LoginForm
  setLoginForm: Dispatch<SetStateAction<LoginForm>>
  onLogin: () => void
}

export default function LoginPanel({
  loginForm,
  setLoginForm,
  onLogin,
}: LoginPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Login</h2>
          <p>Use a customer id or email to continue.</p>
        </div>
      </div>
      <div className="card narrow">
        <label>
          Customer ID
          <input
            value={loginForm.customerId}
            onChange={(event) =>
              setLoginForm((current) => ({
                ...current,
                customerId: event.target.value,
              }))
            }
            placeholder="e.g. 1"
          />
        </label>
        <label>
          Email (optional)
          <input
            value={loginForm.email}
            onChange={(event) =>
              setLoginForm((current) => ({
                ...current,
                email: event.target.value,
              }))
            }
            placeholder="name@store.com"
          />
        </label>
        <button className="primary" onClick={onLogin}>
          Login
        </button>
      </div>
    </section>
  )
}
