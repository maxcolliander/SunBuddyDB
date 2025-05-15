fetch('../users.json')
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

const modal = document.getElementById('addUserModal');
const addUserButton = document.getElementById('addUserButton');
const closeButton = document.querySelector('.close-button');
const addUserForm = document.getElementById('addUserForm');

// Open the modal
addUserButton.addEventListener('click', () => {
  fetch('/get-max-user-id')
    .then(res => res.json())
    .then(data => {
      const maxId = data.max_user_id;
      console.log('Current highest user ID:', maxId);

      // Optionally display next ID
      const nextIdDisplay = document.getElementById('nextUserId');
      if (nextIdDisplay) {
        nextIdDisplay.textContent = `Next User ID: ${maxId + 1}`;
      }

      modal.style.display = 'block';
    })
    .catch(error => {
      console.error('Error fetching max user ID:', error);
      modal.style.display = 'block';  // still open the modal even if it fails
    });
});

// Close the modal
closeButton.addEventListener('click', () => {
  modal.style.display = 'none';
});

// Close the modal when clicking outside of it
window.addEventListener('click', (event) => {
  if (event.target === modal) {
    modal.style.display = 'none';
  }
});

// Handle form submission
addUserForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const userId = document.getElementById('userId').value;
  const skinType = document.getElementById('skinType').value;
  const createdAt = document.getElementById('createdAt').value;

  if (userId && skinType && createdAt) {
    fetch('/add-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        skin_type: skinType,
        created_at: createdAt,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const table = document.getElementById('userTable');

          // Create the main row
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${userId}</td>
            <td>${createdAt}</td>
          `;

          // Create the expandable detail row
          const detailRow = document.createElement('tr');
          detailRow.style.display = 'none';
          detailRow.classList.add('detail-row');
          detailRow.innerHTML = `
            <td colspan="3">
              <div class="user-details">
                <p><strong>Skin Type:</strong> ${skinType}</p>
                <p><strong>Session:</strong> Not available</p>
                <p><strong>Progress:</strong> Not available</p>
                <p><strong>Preferences:</strong> Not available</p>
              </div>
            </td>
          `;

          // Toggle expansion on click
          row.addEventListener('click', () => {
            detailRow.style.display = detailRow.style.display === 'none' ? 'table-row' : 'none';
          });

          // Add both rows to the table
          table.appendChild(row);
          table.appendChild(detailRow);

          modal.style.display = 'none';
          addUserForm.reset();
        } else {
          alert(`Failed to add user: ${data.error}`);
        }
      })
      .catch((error) => {
        console.error('Error adding user:', error);
        alert('Failed to add user.');
      });
  } else {
    alert('All fields are required to add a user.');
  }
});

const randomizeUserButton = document.getElementById('randomizeUserButton');

// Handle randomize user data button click
randomizeUserButton.addEventListener('click', () => {
  fetch('/randomize-user', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
      console.log('Randomized User Data:', data);
     if (data.skin_type && data.created_at) {
        
        // Optionally, populate the form fields with the randomized data
        document.getElementById('skinType').value = data.skin_type;
        document.getElementById('createdAt').value = data.created_at.split(' ');
      } else {
        alert('Incomplete data received from the server.');
      }
    })
    .catch(error => {
      console.error('Error randomizing user data:', error);
      alert('Failed to randomize user data.');
    });
});

addUserForm.addEventListener('submit', (event) => {
  event.preventDefault();

  const skinType = document.getElementById('skinType').value;
  const createdAt = document.getElementById('createdAt').value;

  if (skinType && createdAt) {
    fetch('/add-user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        skin_type: skinType,
        created_at: createdAt,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Add the new user to the table dynamically
          const table = document.getElementById('userTable');
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${createdAt}</td>
            <td>${skinType}</td>
          `;
          table.appendChild(row);

          modal.style.display = 'none';
          addUserForm.reset();
        } else {
          alert(`Failed to add user: ${data.error}`);
        }
      })
      .catch((error) => {
        console.error('Error adding user:', error);
        alert('Failed to add user.');
      });
  } else {
    alert('All fields are required to add a user.');
  }
});

