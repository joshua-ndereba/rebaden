import React from 'react';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav>
        <ul>
          <li className="active">Dashboard</li>
          <li>Events</li>
          <li>Alerts</li>
          <li>Assets</li>
          <li>Settings</li>
        </ul>
      </nav>
    </aside>
  );
}
