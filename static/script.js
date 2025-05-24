// DEFAULT VALUES
const USERS_PER_PAGE = 20;
let currentPage = 1;
let totalUsers = 0;
let sortBy = 'user_id';
let sortOrder = 'asc';

function fetchAndDisplayUsers(page = 1) {
  fetch(`/get-users?page=${page}&limit=${USERS_PER_PAGE}&sort_by=${sortBy}&sort_order=${sortOrder}`)
    .then(res => res.json())
    .then(data => {
      const users = data.users;
      totalUsers = data.total;
      currentPage = data.page;

      const table = document.getElementById('userTable');
      table.innerHTML = '';
      users.forEach(user => {
      let createdAt = user.created_at;
      if (createdAt) {
        const dateObj = new Date(createdAt);
        if (!isNaN(dateObj)) {
          createdAt = dateObj.toISOString().slice(0, 10);
        }
      }
      const row = document.createElement('tr');
      row.style.cursor = 'pointer';
      row.innerHTML = `
        <td>${user.user_id}</td>
        <td>${createdAt}</td>
      `;
      row.addEventListener('click', () => {
        window.location.href = `/user/${user.user_id}`;
      });
      table.appendChild(row);
    });

      renderPagination();
    })
    .catch(error => {
      console.error('Error fetching users:', error);
    });
}

function renderTableHeader() {
  const thead = document.querySelector('#userTable').parentElement.querySelector('thead tr');
  thead.innerHTML = `
    <th id="sortUserId" style="cursor:pointer">User ID ${sortBy === 'user_id' ? (sortOrder === 'asc' ? '▲' : '▼') : ''}</th>
    <th id="sortCreatedAt" style="cursor:pointer">Created At ${sortBy === 'created_at' ? (sortOrder === 'asc' ? '▲' : '▼') : ''}</th>
  `;

  document.getElementById('sortUserId').onclick = () => {
    if (sortBy === 'user_id') {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      sortBy = 'user_id';
      sortOrder = 'asc';
    }
    fetchAndDisplayUsers(1);
    renderTableHeader();
  };

  document.getElementById('sortCreatedAt').onclick = () => {
    if (sortBy === 'created_at') {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      sortBy = 'created_at';
      sortOrder = 'asc';
    }
    fetchAndDisplayUsers(1);
    renderTableHeader();
  };
}

function renderPagination() {
  const pagination = document.getElementById('pagination');
  pagination.innerHTML = '';
  const totalPages = Math.ceil(totalUsers / USERS_PER_PAGE);

  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement('button');
    btn.textContent = i;
    btn.disabled = i === currentPage;
    btn.addEventListener('click', () => fetchAndDisplayUsers(i));
    pagination.appendChild(btn);
  }
}

function loadLeaderboard() {
  fetch('/api/users/average_uv_exposure')
    .then(res => res.json())
    .then(data => {
      const leaderboardTable = document.getElementById('leaderboardTable');
      leaderboardTable.innerHTML = '';

      const topUsers = data.slice(0, 5);

      topUsers.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${user.user_id}</td>
          <td>${user.avg_uv_exposure !== null ? user.avg_uv_exposure : 'N/A'}</td>
        `;
        leaderboardTable.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Error loading leaderboard:', error);
    });
}

window.addEventListener('DOMContentLoaded', () => {
  renderTableHeader();
  fetchAndDisplayUsers();
  loadLeaderboard();
});

const modal = document.getElementById('addUserModal');
const addUserButton = document.getElementById('addUserButton');
const closeButton = document.querySelector('.close-button');
const addUserForm = document.getElementById('addUserForm');

addUserButton.addEventListener('click', () => {
  fetch('/get-max-user-id')
    .then(res => res.json())
    .then(data => {
      const maxId = data.max_user_id;
      console.log('Current highest user ID:', maxId);

      const nextIdDisplay = document.getElementById('nextUserId');
      if (nextIdDisplay) {
        nextIdDisplay.textContent = `Next User ID: ${maxId + 1}`;
      }

      modal.style.display = 'block';
    })
    .catch(error => {
      console.error('Error fetching max user ID:', error);
      modal.style.display = 'block';
    });
});

closeButton.addEventListener('click', () => {
  modal.style.display = 'none';
});

window.addEventListener('click', (event) => {
  if (event.target === modal) {
    modal.style.display = 'none';
  }
});

function handleAddUser(event) {
  event.preventDefault();

  const userIdInput = document.getElementById('userId');
  const skinType = document.getElementById('skinType').value;
  const createdAt = document.getElementById('createdAt').value;
  const userId = userIdInput ? userIdInput.value : null;

  if (skinType && createdAt && (userIdInput ? userId : true)) {
    const payload = { skin_type: skinType, created_at: createdAt };
    if (userIdInput) payload.user_id = userId;

    fetch('/add-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          fetchAndDisplayUsers(currentPage);
          loadLeaderboard();
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
}

addUserForm.addEventListener('submit', handleAddUser);

const randomizeUserButton = document.getElementById('randomizeUserButton');

randomizeUserButton.addEventListener('click', () => {
  fetch('/randomize-user', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
      if (data.skin_type && data.created_at) {
        document.getElementById('skinType').value = data.skin_type;
        document.getElementById('createdAt').value = data.created_at.split(' ')[0];
      } else {
        alert('Incomplete data received from the server.');
      }
    })
    .catch(error => {
      console.error('Error randomizing user data:', error);
      alert('Failed to randomize user data.');
    });
});

