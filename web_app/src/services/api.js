const API_BASE_URL = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Request failed.";
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  return response.json();
}

export const api = {
  loginStudent(rollNo, password) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: rollNo,
        password,
        role: "student",
      }),
    });
  },
  getStudentProfile(rollNo) {
    return request(`/students/${encodeURIComponent(rollNo)}`);
  },
  getStudentAttendanceSummary(rollNo) {
    return request(`/students/${encodeURIComponent(rollNo)}/attendance-summary`);
  },
  getStudentAttendanceRecords(rollNo) {
    return request(`/attendance?roll_no=${encodeURIComponent(rollNo)}`);
  },
  getStudentTimetable(section) {
    return request(`/timetable?section=${encodeURIComponent(section)}`);
  },
};
