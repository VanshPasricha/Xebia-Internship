import { useMemo, useState } from "react";

function InfoCard({ label, value, accent }) {
  return (
    <div className="info-card">
      <p>{label}</p>
      <h3 className={accent ? "accent-text" : ""}>{value}</h3>
    </div>
  );
}

function DataTable({ headers, rows, emptyText }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          {headers.map((header) => (
            <th key={header}>{header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length ? (
          rows.map((row, index) => (
            <tr key={row.id ?? row.subject ?? `${index}-${row[0]}`}>
              {row.map((cell, cellIndex) => (
                <td key={`${index}-${cellIndex}`}>{cell}</td>
              ))}
            </tr>
          ))
        ) : (
          <tr>
            <td colSpan={headers.length}>{emptyText}</td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

function Panel({ title, subtitle, children, wide = false }) {
  return (
    <section className={`panel-card${wide ? " wide" : ""}`}>
      <div className="panel-head">
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

export default function PortalShell({
  student,
  profile,
  attendanceSummary,
  attendanceRecords,
  timetable,
  loading,
  error,
  onLogout,
}) {
  const [activeView, setActiveView] = useState("dashboard");

  const subjectRows = useMemo(
    () =>
      (attendanceSummary?.subject_summaries ?? []).map((row) => [
        row.subject,
        row.present,
        row.total,
        row.percentage,
        row.late_flags,
      ]),
    [attendanceSummary],
  );

  const subjectFlagRows = useMemo(
    () =>
      (attendanceSummary?.subject_summaries ?? []).map((row) => [
        row.subject,
        row.late_flags,
        Math.floor(row.late_flags / 60),
        `${row.percentage}%`,
      ]),
    [attendanceSummary],
  );

  const attendanceRows = useMemo(
    () =>
      attendanceRecords.map((row) => [
        row.date,
        row.subject,
        row.time,
        row.status,
        row.late_flags,
      ]),
    [attendanceRecords],
  );

  const timetableRows = useMemo(
    () =>
      timetable.map((row) => [
        row.day,
        row.subject,
        row.faculty,
        row.section,
        `${row.start_time} - ${row.end_time}`,
      ]),
    [timetable],
  );

  const menuItems = [
    { key: "dashboard", label: "Dashboard" },
    { key: "profile", label: "Profile" },
    { key: "attendance", label: "Attendance" },
    { key: "flags", label: "Flags" },
    { key: "timetable", label: "Timetable" },
  ];

  function renderContent() {
    if (activeView === "profile") {
      return (
        <Panel
          title="Profile"
          subtitle="Student identity and academic information maintained in FACETRACK."
          wide
        >
          <div className="profile-grid">
            <InfoCard label="Roll Number" value={profile?.roll_no ?? "-"} />
            <InfoCard label="Name" value={profile?.name ?? "-"} />
            <InfoCard label="Department" value={profile?.department ?? "-"} />
            <InfoCard label="Year" value={profile?.year ?? "-"} />
            <InfoCard label="Batch" value={profile?.section ?? "-"} />
            <InfoCard label="Total Red Flags" value={profile?.red_flags ?? 0} accent />
          </div>
        </Panel>
      );
    }

    if (activeView === "attendance") {
      return (
        <>
          <Panel
            title="Subject-wise Attendance"
            subtitle="Attendance percentage after late-flag deductions."
            wide
          >
            <DataTable
              headers={["Subject", "Present", "Total", "Attendance %", "Late Flags"]}
              rows={subjectRows}
              emptyText="No subject-wise attendance data available."
            />
          </Panel>
          <Panel
            title="Attendance Records"
            subtitle="Detailed class-wise attendance history."
            wide
          >
            <DataTable
              headers={["Date", "Subject", "Time", "Status", "Late Flags"]}
              rows={attendanceRows}
              emptyText="No attendance records available."
            />
          </Panel>
        </>
      );
    }

    if (activeView === "flags") {
      return (
        <>
          <Panel
            title="Flag Overview"
            subtitle="Late penalties are tracked per subject and rolled into overall deductions."
          >
            <div className="profile-grid">
              <InfoCard label="Current Red Flags" value={profile?.red_flags ?? 0} accent />
              <InfoCard
                label="Equivalent Deductions"
                value={Math.floor((profile?.red_flags ?? 0) / 60)}
              />
            </div>
          </Panel>
          <Panel
            title="Subject-wise Flags"
            subtitle="Flags accumulated for each subject based on late arrival."
            wide
          >
            <DataTable
              headers={["Subject", "Late Flags", "Deductions", "Attendance %"]}
              rows={subjectFlagRows}
              emptyText="No red flag data available."
            />
          </Panel>
        </>
      );
    }

    if (activeView === "timetable") {
      return (
        <Panel
          title="Timetable"
          subtitle="Scheduled classes published for the current batch."
          wide
        >
          <DataTable
            headers={["Day", "Subject", "Faculty", "Batch", "Time"]}
            rows={timetableRows}
            emptyText="No timetable entries available."
          />
        </Panel>
      );
    }

    return (
      <>
        <section className="hero-strip">
          <div>
            <p className="eyebrow">STUDENT DASHBOARD</p>
            <h2>{student.name}</h2>
            <p className="hero-copy">
              Read-only access to attendance, timetable, subject summaries, and
              red flag tracking.
            </p>
          </div>
          <div className="hero-stats">
            <InfoCard
              label="Overall Attendance"
              value={`${attendanceSummary?.overall_percentage ?? 0}%`}
              accent
            />
            <InfoCard label="Total Red Flags" value={profile?.red_flags ?? 0} />
            <InfoCard label="Batch" value={profile?.section ?? "-"} />
          </div>
        </section>

        <section className="content-grid">
          <Panel
            title="Profile Snapshot"
            subtitle="Your current academic identity in FACETRACK."
          >
            <div className="profile-grid">
              <InfoCard label="Roll Number" value={profile?.roll_no ?? "-"} />
              <InfoCard label="Department" value={profile?.department ?? "-"} />
              <InfoCard label="Year" value={profile?.year ?? "-"} />
              <InfoCard label="Batch" value={profile?.section ?? "-"} />
            </div>
          </Panel>

          <Panel
            title="Flag Snapshot"
            subtitle="Latest penalty status across all attendance records."
          >
            <div className="profile-grid">
              <InfoCard label="Current Red Flags" value={profile?.red_flags ?? 0} accent />
              <InfoCard
                label="Subjects Tracked"
                value={(attendanceSummary?.subject_summaries ?? []).length}
              />
            </div>
          </Panel>

          <Panel
            title="Recent Attendance"
            subtitle="Latest recorded class activity."
            wide
          >
            <DataTable
              headers={["Date", "Subject", "Time", "Status", "Late Flags"]}
              rows={attendanceRows.slice(0, 5)}
              emptyText="No attendance records available."
            />
          </Panel>
        </section>
      </>
    );
  }

  return (
    <div className="portal-page">
      <aside className="portal-sidebar">
        <div>
          <div className="logo-badge large">FT</div>
          <h1>FACETRACK</h1>
          <p className="sidebar-copy">Web student portal</p>
        </div>

        <div className="sidebar-card">
          <p className="sidebar-label">Signed in as</p>
          <h3>{student.name}</h3>
          <p>{student.roll_no}</p>
          <p>{profile?.department || "-"}</p>
          <p>
            Year {profile?.year || "-"} | Batch {profile?.section || "-"}
          </p>
        </div>

        <nav className="sidebar-menu">
          {menuItems.map((item) => (
            <button
              key={item.key}
              className={`menu-button${activeView === item.key ? " active" : ""}`}
              onClick={() => setActiveView(item.key)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <button className="secondary-button" onClick={onLogout}>
          Logout
        </button>
      </aside>

      <main className="portal-main">
        {error ? <div className="error-banner">{error}</div> : null}
        {loading ? <div className="loading-banner">Refreshing portal data...</div> : null}
        {renderContent()}
      </main>
    </div>
  );
}
