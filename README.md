# Quester - The Real-Time Q&A Platform for Developers

![Quester Banner](https://placehold.co/1200x300/1e293b/ffffff?text=Quester&font=raleway)

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/status-in%20development-orange.svg" alt="Status">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
</p>

**Quester** is a full-stack, real-time, community-driven platform where developers and tech enthusiasts can ask, browse, and answer technical questions. It's designed with a clean, professional, and easy-to-use interface to make the user experience smooth and efficient.

---

## ✨ Key Features

* **Real-Time Interaction**: See new questions, answers, and comments appear instantly without needing to refresh the page.
* **Smart Voting & Ranking System**: A community-driven, dynamic voting mechanism ensures that the most helpful and accurate answers rise to the top.
* **Structured & Clean UI**: A well-organized format enhances the user experience and makes information easy to find.
* **Secure User Authentication**: OAuth is implemented for secure and seamless user login and registration.
* **Direct Content Sharing**: Easily share specific questions and their answers with a direct link.
* **Focused Community**: The platform is dedicated solely to technical topics, creating a focused environment for developers.

---

## 🛠️ Tech Stack

This project is a full-stack application built with the MERN stack and utilizes WebSockets for real-time communication.

### Frontend
* **React.js**: A powerful JavaScript library for building user interfaces.
* **CSS3**: For styling and creating a modern, responsive design.

### Backend
* **Node.js**: A JavaScript runtime for building the server-side logic.
* **Express.js**: A web application framework for Node.js, used to build our RESTful API.
* **MongoDB**: A NoSQL database used to store user data, questions, answers, and votes.
* **Mongoose**: An ODM (Object Data Modeling) library for MongoDB and Node.js.
* **Socket.IO**: A library that enables real-time, bidirectional, and event-based communication.
* **OAuth 2.0**: For secure user authentication with providers like Google or GitHub.

---

## 🔧 System Architecture

Here is a high-level overview of the application's architecture:

![System Architecture Diagram](https://i.imgur.com/your-architecture-diagram.png) <!-- Upload your architecture diagram to a service like Imgur and paste the link here -->

---

## ⚙️ Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Node.js (v14 or later)
* npm (Node Package Manager)
* MongoDB (local instance or a cloud-based service like MongoDB Atlas)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/quester.git](https://github.com/your-username/quester.git)
    cd quester
    ```

2.  **Install Backend Dependencies:**
    Navigate to the `server` directory and install the required packages.
    ```sh
    cd server
    npm install
    ```

3.  **Install Frontend Dependencies:**
    Navigate to the `client` directory and install the required packages.
    ```sh
    cd ../client
    npm install
    ```

4.  **Set up Environment Variables:**
    In the `server` directory, create a `.env` file and add the following variables.
    ```env
    PORT=5000
    MONGO_URI=your_mongodb_connection_string
    GOOGLE_CLIENT_ID=your_google_oauth_client_id
    GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
    ```

### Running the Application

1.  **Start the Backend Server:**
    From the `server` directory, run:
    ```sh
    npm start
    ```

2.  **Start the Frontend Development Server:**
    From the `client` directory, run:
    ```sh
    npm start
    ```

The application should now be running on `http://localhost:3000`.

---

## 🤝 Meet the Team

This project was a collaborative effort by a dedicated team of developers:

* **Tushar**  
* **Kritika Bhatnagar**
* **Saanvi**
* **Arjun Rahul Ghungrud**
* **Aman Manoj Khode**

Project supervised by **Dr. Anand Motwani**.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

