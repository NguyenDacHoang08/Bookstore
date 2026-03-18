import type { Dispatch, SetStateAction } from 'react'
import type { RegisterForm } from '../types'

type RegisterPanelProps = {
  registerForm: RegisterForm
  setRegisterForm: Dispatch<SetStateAction<RegisterForm>>
  onRegister: () => void
}

export default function RegisterPanel({
  registerForm,
  setRegisterForm,
  onRegister,
}: RegisterPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Register customer</h2>
          <p>Create a customer and auto-create their cart.</p>
        </div>
      </div>
      <div className="card narrow">
        <label>
          Name
          <input
            value={registerForm.name}
            onChange={(event) =>
              setRegisterForm((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
          />
        </label>
        <label>
          Email
          <input
            value={registerForm.email}
            onChange={(event) =>
              setRegisterForm((current) => ({
                ...current,
                email: event.target.value,
              }))
            }
          />
        </label>
        <button className="primary" onClick={onRegister}>
          Create customer
        </button>
      </div>
    </section>
  )
}
