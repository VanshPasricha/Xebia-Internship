export default function LoginScreen({
  form,
  error,
  loading,
  onChange,
  onSubmit,
}) {
  return (
    <div className="login-shell">
      <section className="hero-panel">
        <div className="hero-overlay" />
        <div className="hero-content">
          <p className="eyebrow">FACETRACK STUDENT PORTAL</p>
          <h1>Track attendance, timetable, and red flags from the web.</h1>
          <p className="hero-copy">
            This portal is the web companion to the FACETRACK desktop attendance
            system. Students can view academic status in real time while
            attendance marking remains faculty controlled.
          </p>
        </div>
      </section>

      <section className="login-card">
        <div className="logo-row">
          <div className="logo-badge">FT</div>
          <div>
            <h2>Student Sign In</h2>
            <p>Use your roll number and student password.</p>
          </div>
        </div>

        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            <span>Roll Number</span>
            <input
              name="rollNo"
              value={form.rollNo}
              onChange={onChange}
              placeholder="S24CSEU0001"
              autoComplete="username"
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={onChange}
              placeholder="Enter password"
              autoComplete="current-password"
            />
          </label>

          {error ? <div className="error-banner">{error}</div> : null}

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Open Student Portal"}
          </button>
        </form>
      </section>
    </div>
  );
}
