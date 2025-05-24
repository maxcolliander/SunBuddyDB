window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('userIdDisplay').textContent = userId;

  // Load user info and tan level chart
fetch(`/api/user/${userId}`)
.then(res => res.json())
.then(user => {
  const userDataDiv = document.getElementById('userData');

  // Clear container
  userDataDiv.innerHTML = '';

  if (user.error) {
    userDataDiv.innerHTML = `<em>${user.error}</em>`;
    return;
  }

  // Display skin type
  const skinTypeP = document.createElement('p');
  skinTypeP.innerHTML = `<strong>Skin Type:</strong> ${user.skin_type}`;
  userDataDiv.appendChild(skinTypeP);

  // Create and add canvas container
  const chartContainer = document.createElement('div');
  chartContainer.style.maxWidth = '600px';
  chartContainer.style.marginTop = '20px';
  const canvas = document.createElement('canvas');
  canvas.id = 'tanChart';
  chartContainer.appendChild(canvas);
  userDataDiv.appendChild(chartContainer);

  // Fetch and display progress chart
  fetch(`/api/user/${userId}/progress`)
    .then(res => res.json())
    .then(progressData => {
      if (!progressData || !progressData.length) return;

      const labels = progressData.map(p => new Date(p.date).toLocaleDateString());
      const tanLevels = progressData.map(p => p.tan_level);

      const ctx = canvas.getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Tan Level',
            data: tanLevels,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            tension: 0.2,
            pointRadius: 3,
            pointHoverRadius: 5,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false
          },
          scales: {
            x: {
              title: { display: true, text: 'Date' }
            },
            y: {
              beginAtZero: true,
              suggestedMax: 10,
              title: { display: true, text: 'Tan Level' }
            }
          }
        }
      });
    });
})
.catch(err => {
  console.error('Error loading user info:', err);
  document.getElementById('userData').innerHTML = '<em>Error loading user data.</em>';
});
    

  // Notifications
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

  // UV Exposure
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

    // For buttons in the sessions section to toggle previous/scheduled sessions
    document.getElementById('recordedBtn').addEventListener('click', () => {
      document.getElementById('recordedSessions').classList.remove('hidden');
      document.getElementById('upcomingSessions').classList.add('hidden');
      document.getElementById('recordedBtn').classList.add('active');
      document.getElementById('upcomingBtn').classList.remove('active');
    });
    
    document.getElementById('upcomingBtn').addEventListener('click', () => {
      document.getElementById('recordedSessions').classList.add('hidden');
      document.getElementById('upcomingSessions').classList.remove('hidden');
      document.getElementById('recordedBtn').classList.remove('active');
      document.getElementById('upcomingBtn').classList.add('active');
    });

    document.querySelectorAll('.toggle-details').forEach(btn => {
      btn.addEventListener('click', () => {
        const card = btn.closest('.session-card');
        const details = card.querySelector('.session-details');
        details.classList.toggle('hidden');
        btn.textContent = details.classList.contains('hidden') ? 'Details' : 'Hide';
      });
    });
    fetch(`/api/user/${userId}/sessions`)
    .then(res => res.json())
    .then(sessions => {
      const recordedContainer = document.getElementById('recordedSessions');
      const upcomingContainer = document.getElementById('upcomingSessions');

      recordedContainer.innerHTML = '';
      upcomingContainer.innerHTML = '';

      sessions.forEach(session => {
        const div = document.createElement('div');
        div.className = 'session-card';
        const formatted = new Date(session.date).toLocaleDateString("en-GB", {
          year: "numeric",
          month: "short",
          day: "numeric"
        });
        const summaryHTML = `
          <div class="session-summary" data-session-id="${session.session_id}">
            <span><strong>Location:</strong> ${session.location}</span>
            <span><strong>Date:</strong> ${formatted}</span>
            <button class="toggle-details">Details</button>
          </div>
          <div class="session-details hidden"></div>
        `;

        div.innerHTML = summaryHTML;

        // Append to correct container
        if (session.is_scheduled) {
          upcomingContainer.appendChild(div);
        } else {
          recordedContainer.appendChild(div);
        }
      });


      document.querySelectorAll('.toggle-details').forEach(btn => {
        btn.addEventListener('click', () => {
          const card = btn.closest('.session-card');
          const details = card.querySelector('.session-details');
          const sessionId = card.querySelector('.session-summary').dataset.sessionId;
      
          // If currently hidden, show and fetch if needed
          if (details.classList.contains('hidden')) {
            if (details.innerHTML.trim() === '') {
              fetch(`/api/session/${sessionId}/details`)
                .then(res => res.json())
                .then(data => {
                  const uvObj = JSON.parse(data.uv_index_per_hour);
                  const tempObj = JSON.parse(data.temp_per_hour);
                
                  const labels = [];
                  const uvData = [];
                  const tempData = [];
                  for (let h = 0; h < 24; h++) {
                    labels.push(`${h}:00`);
                    uvData.push(uvObj[h] !== undefined ? uvObj[h] : null);
                    tempData.push(tempObj[h] !== undefined ? tempObj[h] : null);
                  }
                
                  const chartId = `chart-session-${data.session_id}`;
                
                  // Now fetch UV exposure *before* setting the innerHTML
                  fetch(`/api/session/${sessionId}/uv_exposure`)
                    .then(res => res.json())
                    .then(uv => {
                      details.innerHTML = `
                        <p><strong>Start:</strong> ${formatTime(data.start_time)}</p>
                        <p><strong>End:</strong> ${formatTime(data.end_time)}</p>
                        <p><strong>UV Exposure:</strong> ${uv.uv_exposure}</p>
                        <div style="width:100%;max-width:900px;margin:auto;">
                          <canvas id="${chartId}" class="session-chart-canvas"></canvas>
                        </div>
                      `;
                
                      const ctx = document.getElementById(chartId);
                      if (ctx) {
                        new Chart(ctx, {
                          type: 'line',
                          data: {
                            labels: labels,
                            datasets: [
                              {
                                label: 'UV Index',
                                data: uvData,
                                borderColor: 'rgba(255, 99, 132, 1)',
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                tension: 0.2
                              },
                              {
                                label: 'Temperature (°C)',
                                data: tempData,
                                borderColor: 'rgba(54, 162, 235, 1)',
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                tension: 0.2,
                                yAxisID: 'y1'
                              }
                            ]
                          },
                          options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            interaction: {
                              mode: 'index',
                              intersect: false
                            },
                            stacked: false,
                            scales: {
                              x: {
                                title: {
                                  display: true,
                                  text: 'Hour of Day'
                                }
                              },
                              y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                title: {
                                  display: true,
                                  text: 'UV Index'
                                }
                              },
                              y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                title: {
                                  display: true,
                                  text: 'Temperature (°C)'
                                },
                                grid: {
                                  drawOnChartArea: false
                                }
                              }
                            }
                          }
                        });
                      }
                    });
                });
            }
      
            details.classList.remove('hidden');
            btn.textContent = 'Hide';
          } else {
            // Already expanded → hide it
            details.classList.add('hidden');
            btn.textContent = 'Details';
          }
        });
      }); 
      loadNotifications(); 
      document.getElementById('markAllReadBtn').addEventListener('click', () => {
        fetch(`/api/user/${userId}/notifications/read_all`, { method: 'POST' })
          .then(() => loadNotifications());
      });
  });
});

function loadNotifications() {
  fetch(`/api/user/${userId}/notifications`)
    .then(res => res.json())
    .then(notifications => {
      const container = document.getElementById('userNotifications');
      container.innerHTML = '';

      notifications.forEach(n => {
        const div = document.createElement('div');
        div.className = 'notification-item';
        div.innerHTML = `
          <div class="notification-row">
            <div class="notification-content">
              <p><strong>${formatDateTime(n.created_at)}</strong></p>
              <p>${n.message}</p>
            </div>
            <button 
              class="notification-action" 
              data-id="${n.notifications_id}" 
              data-read="${n.is_read ? 'true' : 'false'}">
              ${n.is_read ? 'Delete' : 'Mark as Read'}
            </button>
          </div>
        `;
        container.appendChild(div);
      });

      document.querySelectorAll('.notification-action').forEach(btn => {
        btn.addEventListener('click', () => {
          const id = btn.dataset.id;
          const isReadNow = btn.dataset.read === 'true'; // evaluate on click
      
          const action = isReadNow
            ? fetch(`/api/notification/${id}`, { method: 'DELETE' })
            : fetch(`/api/notification/${id}/read`, { method: 'POST' });
      
          action
            .then(res => {
              if (!res.ok) throw new Error("Failed request");
              return res.json();
            })
            .then(() => loadNotifications())
            .catch(err => console.error("Notification action failed:", err));
        });
      });
    });
}



function formatTime(isoString) {
  const time = new Date(isoString);
  return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDateTime(datetimeString) {
  const d = new Date(datetimeString);
  return d.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}