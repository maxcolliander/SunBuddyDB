window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('userIdDisplay').textContent = userId;

  fetch(`/api/user/${userId}`)
    .then(res => res.json())
    .then(user => {
      if (user.error) {
        document.getElementById('userData').innerHTML = `<em>${user.error}</em>`;
        return;
      }
      document.getElementById('userData').innerHTML = `
        <p><strong>Skin Type:</strong> ${user.skin_type}</p>
        <p><strong>Created At:</strong> ${user.created_at}</p>
      `;
    });

  fetch(`/api/user/${userId}/sessions`)
    .then(res => res.json())
    .then(data => {
      const div = document.getElementById('userSessions');
      if (data.sessions && data.sessions.length) {
        div.innerHTML = data.sessions.map(s =>
          `<div>
            <strong>Date:</strong> ${s.date}, <strong>Start:</strong> ${s.start_time}, <strong>End:</strong> ${s.end_time}, <strong>Location:</strong> ${s.location}
          </div>`
        ).join('');
      } else {
        div.innerHTML = '<em>No sessions found.</em>';
      }
    });

  fetch(`/api/user/${userId}/notifications`)
    .then(res => res.json())
    .then(data => {
      const div = document.getElementById('userNotifications');
      if (data.notifications && data.notifications.length) {
        div.innerHTML = data.notifications.map(n =>
          `<div>
            <strong>${n.created_at}:</strong> ${n.message} ${n.is_read ? '(Read)' : '(Unread)'}
          </div>`
        ).join('');
      } else {
        div.innerHTML = '<em>No notifications found.</em>';
      }
    });

  fetch(`/api/user/${userId}/uv-exposure`)
    .then(res => res.json())
    .then(data => {
      const div = document.getElementById('userUvExposure');
      if (data.avg_uv_exposure !== undefined) {
        div.innerHTML = `<strong>Average UV Exposure:</strong> ${data.avg_uv_exposure}`;
      } else {
        div.innerHTML = '<em>No UV exposure data found.</em>';
      }
    });
});