import { useEffect, useState } from "react";
import LoginScreen from "./components/LoginScreen.jsx";
import PortalShell from "./components/PortalShell.jsx";
import { api } from "./services/api.js";

const STORAGE_KEY = "facetrack-student-session";

function loadStoredSession() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [form, setForm] = useState({ rollNo: "", password: "" });
  const [session, setSession] = useState(loadStoredSession);
  const [profile, setProfile] = useState(null);
  const [attendanceSummary, setAttendanceSummary] = useState(null);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!session?.roll_no) {
      return;
    }

    let active = true;
    setLoading(true);
    setError("");

    Promise.all([
      api.getStudentProfile(session.roll_no),
      api.getStudentAttendanceSummary(session.roll_no),
      api.getStudentAttendanceRecords(session.roll_no),
    ])
      .then(async ([profileResponse, summaryResponse, attendanceResponse]) => {
        const timetableResponse = await api.getStudentTimetable(profileResponse.section);
        if (!active) {
          return;
        }
        setProfile(profileResponse);
        setAttendanceSummary(summaryResponse);
        setAttendanceRecords(attendanceResponse);
        setTimetable(timetableResponse);
      })
      .catch((requestError) => {
        if (!active) {
          return;
        }
        setError(requestError.message || "Unable to load student portal.");
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [session]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.loginStudent(form.rollNo.trim().toUpperCase(), form.password);
      const user = response.user;
      const nextSession = {
        id: user.id,
        roll_no: user.roll_no,
        name: user.name,
      };
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
      setForm({ rollNo: "", password: "" });
    } catch (requestError) {
      setError(requestError.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    window.localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setProfile(null);
    setAttendanceSummary(null);
    setAttendanceRecords([]);
    setTimetable([]);
    setError("");
  }

  if (!session) {
    return (
      <LoginScreen
        form={form}
        error={error}
        loading={loading}
        onChange={handleChange}
        onSubmit={handleSubmit}
      />
    );
  }

  return (
    <PortalShell
      student={session}
      profile={profile}
      attendanceSummary={attendanceSummary}
      attendanceRecords={attendanceRecords}
      timetable={timetable}
      loading={loading}
      error={error}
      onLogout={handleLogout}
    />
  );
}
