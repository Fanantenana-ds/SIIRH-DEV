import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bell } from "lucide-react";
import "./NotificationDropdown.css"; // CSS mifandraika

export default function NotificationDropdown() {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  // Fetch notifications avy amin'ny backend
  const fetchNotifications = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/rh/notifications");
      setNotifications(res.data);
    } catch (error) {
      console.error("Erreur lors de la récupération des notifications:", error);
    }
  };

  useEffect(() => {
    fetchNotifications();
    // Refresh automatique every 30s
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  // Marquer notification ho read
  const markAsRead = async (id) => {
    try {
      await axios.put(`http://127.0.0.1:8000/rh/notifications/${id}/read`);
      // Update local state
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      );
    } catch (error) {
      console.error("Erreur lors de la mise à jour de la notification:", error);
    }
  };

  return (
    <div className="notification-dropdown">
      <button className="bell-btn" onClick={toggleDropdown}>
        <Bell size={24} />
        {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          {notifications.length === 0 ? (
            <div className="no-notifications">Aucune notification</div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                onClick={() => markAsRead(n.id)}
                className={`notification-item ${n.read ? "" : "unread"}`}
              >
                <div className="message">{n.message}</div>
                <small className="date">
                  {new Date(n.date).toLocaleString()}
                </small>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
