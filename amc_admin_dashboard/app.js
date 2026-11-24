document.addEventListener("DOMContentLoaded", () => {
    // API base URL
    const API_BASE = "";

    // DOM Elements
    const usersTableBody = document.getElementById("usersTableBody");
    const searchInput = document.getElementById("searchInput");
    const btnRefresh = document.getElementById("btnRefresh");
    const btnOpenAddModal = document.getElementById("btnOpenAddModal");
    const btnCloseModal = document.getElementById("btnCloseModal");
    const btnCancel = document.getElementById("btnCancel");
    const userModal = document.getElementById("userModal");
    const userForm = document.getElementById("userForm");
    const modalTitle = document.getElementById("modalTitle");
    const formMode = document.getElementById("formMode");
    const telegramIdInput = document.getElementById("telegramId");
    const registerNoInput = document.getElementById("registerNo");
    const dobInput = document.getElementById("dob");
    const submitBtnText = document.getElementById("submitBtnText");
    const btnSpinner = document.querySelector(".btn-spinner");
    const btnSubmit = document.getElementById("btnSubmit");
    
    // Stats elements
    const statTotalUsers = document.getElementById("statTotalUsers");
    const statActiveDepts = document.getElementById("statActiveDepts");

    // Local Users Cache
    let usersData = [];

    // Initialize Toast Notifications
    function showToast(message, type = "success") {
        const container = document.getElementById("toastContainer");
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        
        const icon = type === "success" ? "fa-circle-check" : "fa-circle-exclamation";
        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Remove toast after 4 seconds
        setTimeout(() => {
            toast.style.animation = "toast-in 0.3s ease reverse forwards";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Fetch and Load Users
    async function loadUsers() {
        showLoadingState();
        try {
            const response = await fetch(`${API_BASE}/api/users`);
            const result = await response.json();
            
            if (result.success) {
                usersData = result.users;
                renderUsers(usersData);
                updateStats(usersData);
            } else {
                showToast(result.error || "Failed to fetch users", "error");
                showEmptyState("Error loading data");
            }
        } catch (error) {
            showToast("Server connection error", "error");
            showEmptyState("Network Connection Error");
        }
    }

    // Update Dashboard Stats Card numbers
    function updateStats(users) {
        statTotalUsers.innerText = users.length;
        const departments = new Set(
            users.map(u => u.department_name).filter(d => d && d !== "Not Cached" && d !== "")
        );
        statActiveDepts.innerText = departments.size;
    }

    // Show Loading Spinner Row
    function showLoadingState() {
        usersTableBody.innerHTML = `
            <tr class="loading-row">
                <td colspan="7">
                    <div class="spinner-loader"></div>
                    <span>Fetching user profiles...</span>
                </td>
            </tr>
        `;
    }

    // Show Empty Info Row
    function showEmptyState(msg = "No users registered yet.") {
        usersTableBody.innerHTML = `
            <tr class="empty-row">
                <td colspan="7">
                    <i class="fa-solid fa-users-slash" style="font-size: 24px; margin-bottom: 8px; display: block; color: var(--text-secondary);"></i>
                    <span>${msg}</span>
                </td>
            </tr>
        `;
    }

    // Render User Records in Table
    function renderUsers(users) {
        if (users.length === 0) {
            showEmptyState();
            return;
        }

        usersTableBody.innerHTML = "";
        users.forEach(user => {
            const tr = document.createElement("tr");
            
            const deptText = user.department_name && user.department_name !== "Not Cached"
                ? `${user.course_name} <span class="student-email-val">${user.department_name}</span>`
                : `<span class="badge badge-outline">Unsynced</span>`;

            const yearText = user.semester 
                ? `Year ${user.college_year} <span class="student-email-val">Sem ${user.semester} (${user.batch})</span>`
                : "—";

            tr.innerHTML = `
                <td>
                    <div class="user-telegram-cell">
                        <i class="fa-brands fa-telegram"></i>
                        <span>${user.telegram_id}</span>
                    </div>
                </td>
                <td>
                    <span class="student-name-val">${user.student_name}</span>
                    <span class="student-email-val">${user.email || "No Email"}</span>
                </td>
                <td><code>${user.register_no}</code></td>
                <td><code>${user.dob}</code></td>
                <td>${deptText}</td>
                <td>${yearText}</td>
                <td class="actions-col">
                    <div class="action-buttons-group">
                        <button class="btn-action edit" data-id="${user.telegram_id}" title="Edit User">
                            <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                        <button class="btn-action delete" data-id="${user.telegram_id}" title="Delete User">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </td>
            `;

            // Bind Event Listeners on newly added action buttons
            tr.querySelector(".edit").addEventListener("click", () => openEditModal(user));
            tr.querySelector(".delete").addEventListener("click", () => deleteUser(user.telegram_id));

            usersTableBody.appendChild(tr);
        });
    }

    // Filter Users by Search Box input
    searchInput.addEventListener("input", (e) => {
        const term = e.target.value.toLowerCase().trim();
        if (!term) {
            renderUsers(usersData);
            return;
        }

        const filtered = usersData.filter(user => 
            String(user.telegram_id).toLowerCase().includes(term) ||
            user.student_name.toLowerCase().includes(term) ||
            user.register_no.toLowerCase().includes(term) ||
            user.email.toLowerCase().includes(term) ||
            user.department_name.toLowerCase().includes(term)
        );
        renderUsers(filtered);
    });

    // Delete User record
    async function deleteUser(telegramId) {
        if (!confirm(`Are you sure you want to delete user ${telegramId}? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/api/users/delete`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ telegram_id: telegramId })
            });
            const result = await response.json();
            
            if (result.success) {
                showToast("User deleted successfully!");
                loadUsers();
            } else {
                showToast(result.error || "Failed to delete user", "error");
            }
        } catch (error) {
            showToast("Server connection error during delete", "error");
        }
    }

    // Modal Control Logic
    function openAddModal() {
        modalTitle.innerText = "Add New User";
        formMode.value = "add";
        telegramIdInput.value = "";
        telegramIdInput.disabled = false;
        registerNoInput.value = "";
        dobInput.value = "";
        submitBtnText.innerText = "Save & Verify";
        userModal.classList.add("active");
    }

    function openEditModal(user) {
        modalTitle.innerText = `Edit User Details`;
        formMode.value = "update";
        telegramIdInput.value = user.telegram_id;
        telegramIdInput.disabled = true; // Block Telegram ID updates since it acts as the primary key
        registerNoInput.value = user.register_no === "N/A" ? "" : user.register_no;
        dobInput.value = user.dob === "N/A" ? "" : user.dob;
        submitBtnText.innerText = "Update & Verify";
        userModal.classList.add("active");
    }

    function closeModal() {
        userModal.classList.remove("active");
        userForm.reset();
    }

    btnOpenAddModal.addEventListener("click", openAddModal);
    btnCloseModal.addEventListener("click", closeModal);
    btnCancel.addEventListener("click", closeModal);
    btnRefresh.addEventListener("click", loadUsers);

    // Form Submission (Add & Update)
    userForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const mode = formMode.value;
        const telegramId = telegramIdInput.value;
        const registerNo = registerNoInput.value.trim();
        const dob = dobInput.value.trim();

        // DOB Format Regex validation (YYYY-MM-DD)
        const dobRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dobRegex.test(dob)) {
            showToast("DOB must match YYYY-MM-DD format!", "error");
            return;
        }

        // Toggle Loading indicators
        btnSubmit.disabled = true;
        btnSpinner.classList.remove("hidden");

        const endpoint = mode === "add" ? "/api/users/add" : "/api/users/update";

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    telegram_id: telegramId,
                    register_no: registerNo,
                    dob: dob
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showToast(
                    mode === "add" 
                        ? `User '${result.student_name}' registered successfully!` 
                        : "User updated successfully!"
                );
                closeModal();
                loadUsers();
            } else {
                showToast(result.error || "Failed to save user", "error");
            }
        } catch (error) {
            showToast("Connection timed out. Server unreachable.", "error");
        } finally {
            btnSubmit.disabled = false;
            btnSpinner.classList.add("hidden");
        }
    });

    // Initial load
    loadUsers();
});
