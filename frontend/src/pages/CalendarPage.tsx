import { useEffect, useMemo, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import type { DateClickArg } from "@fullcalendar/interaction";
import type { EventClickArg } from "@fullcalendar/core";

import {
  createEvent,
  deleteEvent,
  getEvents,
  getProfile,
  respondToInvite,
  updateEvent,
  type Event,
  type EventAttendee,
} from "../api";

type EventForm = {
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location: string;
};

const emptyForm: EventForm = {
  title: "",
  description: "",
  start_time: "",
  end_time: "",
  location: "",
};

export default function CalendarPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [myUserId, setMyUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState<EventForm>(emptyForm);
  const [pendingInviteUsers, setPendingInviteUsers] = useState("");

  async function loadCalendarData(): Promise<Event[] | null> {
    setLoading(true);
    setError("");
    try {
      const [profile, eventRows] = await Promise.all([getProfile(), getEvents()]);
      setMyUserId(profile.id);
      setEvents(eventRows);
      return eventRows;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load calendar data");
      return null;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCalendarData();
  }, []);

  const calendarEvents = useMemo(
    () =>
      events.map((event) => ({
        id: String(event.id),
        title: event.title,
        start: event.start_time,
        end: event.end_time,
        classNames: [getEventClassName(event, myUserId)],
      })),
    [events, myUserId]
  );

  const upcomingMyEvents = useMemo(() => {
    if (myUserId == null) return [];
    const now = Date.now();
    return events
      .filter((e) => e.creator_id === myUserId && new Date(e.end_time).getTime() >= now)
      .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
  }, [events, myUserId]);

  const upcomingInvitedEvents = useMemo(() => {
    if (myUserId == null) return [];
    const now = Date.now();
    return events
      .filter(
        (e) =>
          e.creator_id !== myUserId &&
          (e.attendees?.some((a) => a.user_id === myUserId) ?? false) &&
          new Date(e.end_time).getTime() >= now
      )
      .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
  }, [events, myUserId]);

  function openEventDetail(event: Event) {
    setSelectedEvent(event);
    setIsEditing(false);
    setForm({
      title: event.title ?? "",
      description: event.description ?? "",
      start_time: toLocalInputDateTime(event.start_time),
      end_time: toLocalInputDateTime(event.end_time),
      location: event.location ?? "",
    });
    setShowDetailModal(true);
  }

  function handleDateClick(arg: DateClickArg) {
    const start = `${arg.dateStr}T09:00`;
    const end = `${arg.dateStr}T10:00`;
    setForm({
      ...emptyForm,
      start_time: start,
      end_time: end,
    });
    setShowCreateModal(true);
  }

  function handleEventClick(arg: EventClickArg) {
    const clicked = events.find((event) => event.id === Number(arg.event.id));
    if (!clicked) return;
    openEventDetail(clicked);
  }

  async function handleCreateSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await createEvent({
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
        location: form.location.trim() || undefined,
        invite_user_ids: [],
      });
      setShowCreateModal(false);
      setForm(emptyForm);
      await loadCalendarData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create event");
    }
  }

  async function handleUpdateSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedEvent) return;
    setError("");
    try {
      const updated = await updateEvent(selectedEvent.id, {
        title: form.title.trim(),
        description: form.description.trim() || undefined,
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
        location: form.location.trim() || undefined,
      });
      setSelectedEvent(updated);
      setIsEditing(false);
      await loadCalendarData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update event");
    }
  }

  async function handleDelete() {
    if (!selectedEvent) return;
    if (!window.confirm("Delete this event?")) return;
    setError("");
    try {
      await deleteEvent(selectedEvent.id);
      setShowDetailModal(false);
      setSelectedEvent(null);
      await loadCalendarData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete event");
    }
  }

  async function handleRespond(status: "accepted" | "declined") {
    if (!selectedEvent) return;
    setError("");
    try {
      await respondToInvite(selectedEvent.id, status);
      const nextEvents = await loadCalendarData();
      const refreshed = nextEvents?.find((event) => event.id === selectedEvent.id);
      if (refreshed) setSelectedEvent(refreshed);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update invitation");
    }
  }

  const isCreator = selectedEvent && myUserId !== null ? selectedEvent.creator_id === myUserId : false;
  const myAttendeeRow = selectedEvent?.attendees?.find((a) => a.user_id === myUserId) ?? null;

  return (
    <div style={{ padding: "20px" }}>
      <div style={styles.headerRow}>
        <h2 style={{ margin: 0 }}>Calendar</h2>
        <button className="new-habit-btn" onClick={() => setShowCreateModal(true)}>
          + New Event
        </button>
      </div>

      {error && <p style={styles.errorText}>{error}</p>}

      {loading ? (
        <p>Loading calendar...</p>
      ) : (
        <>
          <div className="calendar-wrap">
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView="dayGridMonth"
              headerToolbar={{
                left: "prev,next today",
                center: "title",
                right: "dayGridMonth,timeGridWeek,timeGridDay",
              }}
              buttonText={{ month: "Month", week: "Week", day: "Day", today: "Today" }}
              events={calendarEvents}
              dateClick={handleDateClick}
              eventClick={handleEventClick}
              height="auto"
            />
          </div>

          <div className="calendar-lists-grid">
            <section className="calendar-list-section">
              <h3>Upcoming events</h3>
              <p className="calendar-list-sub">Events you created, starting soonest first.</p>
              {upcomingMyEvents.length === 0 ? (
                <p className="calendar-list-empty">No upcoming events you created.</p>
              ) : (
                upcomingMyEvents.map((event) => (
                  <button
                    key={event.id}
                    type="button"
                    className="calendar-event-card"
                    onClick={() => openEventDetail(event)}
                  >
                    <p className="calendar-event-card-title">{event.title}</p>
                    <p className="calendar-event-card-meta">
                      {formatDateRange(event.start_time, event.end_time)}
                    </p>
                    {event.location ? (
                      <p className="calendar-event-card-meta">📍 {event.location}</p>
                    ) : null}
                    {event.description ? (
                      <p className="calendar-event-card-desc">{event.description}</p>
                    ) : null}
                    <p className="calendar-event-card-meta" style={{ marginTop: "0.45rem" }}>
                      <span className={`event-status-badge ${getEventClassName(event, myUserId)}`}>
                        {getEventStatusLabel(event, myUserId)}
                      </span>
                    </p>
                  </button>
                ))
              )}
            </section>

            <section className="calendar-list-section">
              <h3>You&apos;re invited to</h3>
              <p className="calendar-list-sub">Events you are invited to.</p>
              {upcomingInvitedEvents.length === 0 ? (
                <p className="calendar-list-empty">No upcoming invitations.</p>
              ) : (
                upcomingInvitedEvents.map((event) => (
                  <button
                    key={event.id}
                    type="button"
                    className="calendar-event-card"
                    onClick={() => openEventDetail(event)}
                  >
                    <p className="calendar-event-card-title">{event.title}</p>
                    <p className="calendar-event-card-meta">
                      {formatDateRange(event.start_time, event.end_time)}
                    </p>
                    {event.location ? (
                      <p className="calendar-event-card-meta">📍 {event.location}</p>
                    ) : null}
                    {event.description ? (
                      <p className="calendar-event-card-desc">{event.description}</p>
                    ) : null}
                    <p className="calendar-event-card-meta" style={{ marginTop: "0.45rem" }}>
                      <span className={`event-status-badge ${getEventClassName(event, myUserId)}`}>
                        {getEventStatusLabel(event, myUserId)}
                      </span>
                    </p>
                  </button>
                ))
              )}
            </section>
          </div>
        </>
      )}

      {showCreateModal && (
        <div style={modalStyles.overlay}>
          <div style={modalStyles.content}>
            <h3>Create Event</h3>
            <form onSubmit={handleCreateSubmit} style={styles.form}>
              <input
                style={styles.input}
                placeholder="Title (required)"
                value={form.title}
                onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
                required
              />
              <textarea
                style={{ ...styles.input, minHeight: "80px" }}
                placeholder="Description"
                value={form.description}
                onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              />
              <input
                style={styles.input}
                type="datetime-local"
                value={form.start_time}
                onChange={(e) => setForm((prev) => ({ ...prev, start_time: e.target.value }))}
                required
              />
              <input
                style={styles.input}
                type="datetime-local"
                value={form.end_time}
                onChange={(e) => setForm((prev) => ({ ...prev, end_time: e.target.value }))}
                required
              />
              <input
                style={styles.input}
                placeholder="Location"
                value={form.location}
                onChange={(e) => setForm((prev) => ({ ...prev, location: e.target.value }))}
              />
              <input
                style={styles.input}
                placeholder="Invite users (placeholder: teammate will connect social/friends)"
                value={pendingInviteUsers}
                onChange={(e) => setPendingInviteUsers(e.target.value)}
              />
              <div style={styles.btnRow}>
                <button className="new-habit-btn" type="submit">
                  Save Event
                </button>
                <button type="button" style={styles.cancelBtn} onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDetailModal && selectedEvent && (
        <div style={modalStyles.overlay}>
          <div style={modalStyles.content}>
            <h3>{isEditing ? "Edit Event" : selectedEvent.title}</h3>

            {isEditing ? (
              <form onSubmit={handleUpdateSubmit} style={styles.form}>
                <input
                  style={styles.input}
                  value={form.title}
                  onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
                  required
                />
                <textarea
                  style={{ ...styles.input, minHeight: "80px" }}
                  value={form.description}
                  onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
                />
                <input
                  style={styles.input}
                  type="datetime-local"
                  value={form.start_time}
                  onChange={(e) => setForm((prev) => ({ ...prev, start_time: e.target.value }))}
                  required
                />
                <input
                  style={styles.input}
                  type="datetime-local"
                  value={form.end_time}
                  onChange={(e) => setForm((prev) => ({ ...prev, end_time: e.target.value }))}
                  required
                />
                <input
                  style={styles.input}
                  value={form.location}
                  onChange={(e) => setForm((prev) => ({ ...prev, location: e.target.value }))}
                  placeholder="Location"
                />
                <div style={styles.btnRow}>
                  <button className="new-habit-btn" type="submit">
                    Update
                  </button>
                  <button type="button" style={styles.cancelBtn} onClick={() => setIsEditing(false)}>
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div style={styles.detailStack}>
                <p><strong>Description:</strong> {selectedEvent.description || "No description"}</p>
                <p><strong>Start:</strong> {formatDateTime(selectedEvent.start_time)}</p>
                <p><strong>End:</strong> {formatDateTime(selectedEvent.end_time)}</p>
                <p><strong>Location:</strong> {selectedEvent.location || "No location"}</p>
                <p>
                  <strong>Status:</strong>{" "}
                  <span className={`event-status-badge ${getEventClassName(selectedEvent, myUserId)}`}>
                    {getEventStatusLabel(selectedEvent, myUserId)}
                  </span>
                </p>

                <div>
                  <strong>Attendees</strong>
                  {selectedEvent.attendees?.length ? (
                    <ul style={styles.attendeeList}>
                      {selectedEvent.attendees.map((attendee: EventAttendee) => (
                        <li key={`${attendee.user_id}-${attendee.id ?? "n/a"}`}>
                          {attendee.user?.username ?? `User #${attendee.user_id}`} - {attendee.status}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ marginTop: "8px", color: "#777" }}>No attendees yet.</p>
                  )}
                </div>

                {!isCreator && myAttendeeRow && (
                  <div style={styles.btnRow}>
                    <button className="new-habit-btn" onClick={() => handleRespond("accepted")}>
                      Accept
                    </button>
                    <button style={styles.declineBtn} onClick={() => handleRespond("declined")}>
                      Decline
                    </button>
                  </div>
                )}

                {isCreator && (
                  <div style={styles.btnRow}>
                    <button className="new-habit-btn" onClick={() => setIsEditing(true)}>
                      Edit
                    </button>
                    <button style={styles.deleteBtn} onClick={handleDelete}>
                      Delete
                    </button>
                  </div>
                )}

                <div style={styles.btnRow}>
                  <button
                    type="button"
                    style={styles.cancelBtn}
                    onClick={() => {
                      setShowDetailModal(false);
                      setSelectedEvent(null);
                    }}
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function formatDateTime(dateValue: string) {
  return new Date(dateValue).toLocaleString();
}

function formatDateRange(start: string, end: string) {
  const s = new Date(start);
  const e = new Date(end);
  const sameDay =
    s.getFullYear() === e.getFullYear() &&
    s.getMonth() === e.getMonth() &&
    s.getDate() === e.getDate();
  if (sameDay) {
    const dayPart = s.toLocaleDateString(undefined, {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
    const t1 = s.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
    const t2 = e.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
    return `${dayPart} · ${t1} – ${t2}`;
  }
  return `${formatDateTime(start)} → ${formatDateTime(end)}`;
}

function toLocalInputDateTime(dateValue: string) {
  const date = new Date(dateValue);
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - offset * 60000);
  return localDate.toISOString().slice(0, 16);
}

function getEventClassName(event: Event, myUserId: number | null) {
  if (!myUserId) return "event-created";
  if (event.creator_id === myUserId) return "event-created";
  const mine = event.attendees?.find((attendee) => attendee.user_id === myUserId);
  if (!mine || mine.status === "invited") return "event-invited";
  if (mine.status === "accepted") return "event-accepted";
  return "event-declined";
}

function getEventStatusLabel(event: Event, myUserId: number | null) {
  if (!myUserId) return "Created";
  if (event.creator_id === myUserId) return "Created by you";
  const mine = event.attendees?.find((attendee) => attendee.user_id === myUserId);
  if (!mine || mine.status === "invited") return "Invited (pending)";
  if (mine.status === "accepted") return "Accepted";
  return "Declined";
}

const styles: Record<string, React.CSSProperties> = {
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
  },
  errorText: {
    color: "#b91c1c",
    marginBottom: "12px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  input: {
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "0.95rem",
  },
  btnRow: {
    display: "flex",
    gap: "10px",
    marginTop: "6px",
  },
  cancelBtn: {
    flex: 1,
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    background: "white",
    cursor: "pointer",
  },
  deleteBtn: {
    flex: 1,
    padding: "10px",
    borderRadius: "8px",
    border: "none",
    background: "#dc2626",
    color: "white",
    cursor: "pointer",
  },
  declineBtn: {
    flex: 1,
    padding: "10px",
    borderRadius: "8px",
    border: "none",
    background: "#6b7280",
    color: "white",
    cursor: "pointer",
  },
  detailStack: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  attendeeList: {
    paddingLeft: "18px",
    marginTop: "8px",
  },
};

const modalStyles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: "16px",
  },
  content: {
    width: "100%",
    maxWidth: "520px",
    maxHeight: "90vh",
    overflowY: "auto",
    backgroundColor: "white",
    borderRadius: "12px",
    padding: "20px",
    boxShadow: "0 10px 24px rgba(0,0,0,0.2)",
  },
};
