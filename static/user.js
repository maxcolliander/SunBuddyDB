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

  fetch(`/api/user/${userId}/preferences`)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('userPreferences');
      if (data && Object.keys(data).length > 0) {
        container.innerHTML = `
          <label><strong>Minimum time for a session (minutes):</strong>
            <input type="number" value="${data.min_time}" id="min_time" min="15" max="240">
          </label><br>

          <label><strong>Maximum time for a session (minutes):</strong>
            <input type="number" value="${data.max_time}" id="max_time" min="30" max="480">
          </label><br>

          <label><strong>How imporant is the length of the session? (1-3)</strong>
            <input type="number" value="${data.weight_time}" id="weight_time" min="1" max="3">
          </label><br>

          <label><strong>Minimum temperature for a session:</strong>
            <input type="number" value="${data.min_temp}" id="min_temp" min="0" max="20">
          </label><br>

          <label><strong>Maximum temperature for a session:</strong>
            <input type="number" value="${data.max_temp}" id="max_temp" min="10" max="40">
          </label><br>

          <label><strong>How imporant are the outside temperatures during the session? (1-3)</strong>
            <input type="number" value="${data.weight_temp}" id="weight_temp" min="1" max="3">
          </label><br>

          <label><strong>Minimum UV for a session:</strong>
            <input type="number" value="${data.min_uv}" id="min_uv" min="0" max="5">
          </label><br>

          <label><strong>Maximum UV for a session:</strong>
            <input type="number" value="${data.max_uv}" id="max_uv" min="2" max="14">
          </label><br>

          <label><strong>How imporant are the UV-levels during the session? (1-3)</strong>
            <input type="number" value="${data.weight_uv}" id="weight_uv" min="1" max="3">
          </label><br>
        `;
        document.querySelectorAll('#userPreferences input[type="number"]').forEach(input => {
          input.addEventListener('blur', () => {
            const value = parseFloat(input.value);
            const min = parseFloat(input.min);
            const max = parseFloat(input.max);
    
            if (value < min) input.value = min;
            else if (value > max) input.value = max;
          });
        });
        let originalValues = {
          min_time: parseInt(data.min_time),
          max_time: parseInt(data.max_time),
          weight_time: parseInt(data.weight_time),
          min_temp: parseInt(data.min_temp),
          max_temp: parseInt(data.max_temp),
          weight_temp: parseInt(data.weight_temp),
          min_uv: parseInt(data.min_uv),
          max_uv: parseInt(data.max_uv),
          weight_uv: parseInt(data.weight_uv)
        };
        // Watch for changes
        document.querySelectorAll('#userPreferences input').forEach(input => {
          input.addEventListener('input', () => {
            showSnackbar();
          });
        });

        // Show snackbar
        function showSnackbar() {
          const bar = document.getElementById('preferenceSnackbar');
          bar.classList.remove('hidden');
        }

        document.getElementById('savePrefs').addEventListener('click', () => {
          const updatedPreferences = {
            min_time: parseInt(document.getElementById('min_time').value),
            max_time: parseInt(document.getElementById('max_time').value),
            weight_time: parseInt(document.getElementById('weight_time').value),
            min_temp: parseInt(document.getElementById('min_temp').value),
            max_temp: parseInt(document.getElementById('max_temp').value),
            weight_temp: parseInt(document.getElementById('weight_temp').value),
            min_uv: parseInt(document.getElementById('min_uv').value),
            max_uv: parseInt(document.getElementById('max_uv').value),
            weight_uv: parseInt(document.getElementById('weight_uv').value)
          };
        
          fetch(`/api/user/${userId}/preferences`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedPreferences)
          })
            .then(response => {
              if (response.ok) {
                document.getElementById('preferenceSnackbar').classList.add('hidden');
                // Update stored original values
                originalValues = { ...updatedPreferences };
              } else {
                alert('Failed to save preferences.');
              }
            })
            .catch(error => {
              console.error('Error saving preferences:', error);
              alert('Error occurred while saving.');
            });
        });

        // Discard button handler
        document.getElementById('discardPrefs').addEventListener('click', () => {
          // Reset all inputs to original values
          for (const key in originalValues) {
            const el = document.getElementById(key);
            if (el) el.value = originalValues[key];
          }
          document.getElementById('preferenceSnackbar').classList.add('hidden');
        });
      } else {
        container.textContent = "No preferences data available.";
      }
    })
    .catch(error => {
      document.getElementById('userPreferences').textContent = "Error loading preferences.";
      console.error("Preferences fetch error:", error);
    });
});