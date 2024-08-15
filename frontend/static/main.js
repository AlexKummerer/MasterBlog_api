let authToken = null;

// Function that runs once the window is fully loaded
window.onload = function () {
  var savedBaseUrl = localStorage.getItem("apiBaseUrl");
  if (savedBaseUrl) {
    document.getElementById("api-base-url").value = savedBaseUrl;
    loadPosts();
  }
};

// Function to handle user registration
function register() {
  const baseUrl = document.getElementById("api-base-url").value;
  const username = document.getElementById("reg-username").value;
  const password = document.getElementById("reg-password").value;

  fetch(baseUrl + "/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: username, password: password }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message) {
        console.log("Registration successful:", data.message);
        alert("Registration successful! You can now log in.");
      } else {
        console.error("Registration failed:", data.error);
        alert("Registration failed: " + data.error);
      }
    })
    .catch((error) => console.error("Error:", error));
}

function login() {
  const baseUrl = document.getElementById("api-base-url").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  fetch(baseUrl + "/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: username, password: password }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.access_token) {
        authToken = data.access_token;
        console.log("Login successful");

        // Fetch the logged-in user's username
        fetch(baseUrl + "/user", {
          headers: { Authorization: "Bearer " + authToken },
        })
          .then((response) => response.json())
          .then((userData) => {
            loggedInUsername = userData.username;
            console.log("Logged in as:", loggedInUsername);
            loadPosts(); // Load posts after getting the username
          });
      } else {
        console.error("Login failed:", data.error);
        alert("Login failed: " + data.error);
      }
    })
    .catch((error) => console.error("Error:", error));
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
  const baseUrl = document.getElementById("api-base-url").value;
  localStorage.setItem("apiBaseUrl", baseUrl);

  fetch(baseUrl + "/v1/posts", {
    headers: { Authorization: "Bearer " + authToken },
  })
    .then((response) => response.json())
    .then((data) => {
      const postContainer = document.getElementById("post-container");
      postContainer.innerHTML = "";

      data.results.forEach((post) => {
        const postDiv = document.createElement("div");
        postDiv.className = "post";
        postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <p><strong>Author:</strong> ${
                      post.author
                    } | <strong>Date:</strong> ${new Date(
          post.date
        ).toLocaleString()}</p>
                    <button onclick="deletePost('${post.id}')">Delete</button>`;
        postContainer.appendChild(postDiv);
      });
    })
    .catch((error) => console.error("Error:", error));
}

// Function to send a POST request to the API to add a new post
function addPost() {
  const baseUrl = document.getElementById("api-base-url").value;
  const postTitle = document.getElementById("post-title").value;
  const postContent = document.getElementById("post-content").value;

  fetch(baseUrl + "/v1/posts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + authToken,
    },
    body: JSON.stringify({
      title: postTitle,
      content: postContent,
      author: loggedInUsername,
    }), // Use the logged-in user's name
  })
    .then((response) => response.json())
    .then((post) => {
      console.log("Post added:", post);
      loadPosts(); // Reload the posts after adding a new one
    })
    .catch((error) => console.error("Error:", error));
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
  const baseUrl = document.getElementById("api-base-url").value;

  fetch(baseUrl + "/v1/posts/" + postId, {
    method: "DELETE",
    headers: { Authorization: "Bearer " + authToken },
  })
    .then((response) => {
      console.log("Post deleted:", postId);
      loadPosts(); // Reload the posts after deleting one
    })
    .catch((error) => console.error("Error:", error));
}
