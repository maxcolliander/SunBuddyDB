fetch('users.json')
  .then(res => res.json())
  .then(users => {
    const table = document.getElementById('userTable');

    users.forEach((user, index) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${user.user_id}</td>
        <td>${user.created_at.split(" ")[0]}</td>
        <td>${user.session.location}</td>
      `;

      // Create expandable detail row
      const detailRow = document.createElement('tr');
      detailRow.style.display = 'none';
      detailRow.classList.add('detail-row');
      detailRow.innerHTML = `
        <td colspan="3">
          <div class="user-details">
            <p><strong>Skin Type:</strong> ${user.skin_type}</p>
            <p><strong>Session:</strong> ${user.session.start_time} – ${user.session.end_time}</p>
            <p><strong>Progress:</strong> Tan level ${user.progress.tan_level} on ${user.progress.date}</p>
            <p><strong>Preferences:</strong> UV ${user.preferences.min_uv}–${user.preferences.max_uv}, Temp ${user.preferences.min_temp}–${user.preferences.max_temp}°C, Time ${user.preferences.min_time}–${user.preferences.max_time} min</p>
          </div>
        </td>
      `;

      // Toggle expansion on click
      row.addEventListener('click', () => {
        detailRow.style.display = detailRow.style.display === 'none' ? 'table-row' : 'none';
      });

      // Add both rows
      table.appendChild(row);
      table.appendChild(detailRow);
    });
  })
  .catch(err => {
    console.error("Failed to load users.json:", err);
  });