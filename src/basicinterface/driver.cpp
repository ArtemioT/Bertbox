#include <iostream>
#include <thread>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/wait.h>

pid_t flask_pid = -1;
int server_fd = -1;
bool running = true;

// ---- Function to start Flask ----
void start_flask() {
    flask_pid = fork();
    if (flask_pid == 0) {
        std::cout << "Starting Flask...\n";
        execlp("python3", "python3", "app.py", nullptr);
        perror("Failed to start Flask");
        _exit(1);
    } else if (flask_pid < 0) {
        perror("Fork failed");
        exit(1);
    } else {
        std::cout << "Flask started with PID " << flask_pid << "\n";
    }
}

// ---- Function to stop Flask ----
void stop_flask(int) {
    running = false;
    std::cout << "\nShutting down...\n";
    if (flask_pid > 0) {
        std::cout << "Stopping Flask (PID " << flask_pid << ")...\n";
        kill(flask_pid, SIGTERM);
        waitpid(flask_pid, nullptr, 0);
    }
    if (server_fd > 0) close(server_fd);
    std::cout << "Exiting main program.\n";
    exit(0);
}

// ---- Function to handle incoming Flask messages ----
void handle_client(int client_socket) {
    char buffer[1024];
    int bytes_read = read(client_socket, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        std::string message(buffer);

        std::cout << "[Received] " << message << std::endl;

        // Example: handle specific commands
        if (message == "START_PUMP") {
            std::cout << "→ Turning pump ON\n";
            system("python ultrasonic.py");
            // system("python3 pump_on.py");  // example: run script
        } else if (message == "STOP_PUMP") {
            std::cout << "→ Turning pump OFF\n";
            // system("python3 pump_off.py");
        } else {
            std::cout << "→ Unknown command.\n";
        }
    }
    close(client_socket);
}

// ---- TCP server to listen for Flask commands ----
void start_listener(int port = 6000) {
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("Socket creation failed");
        exit(1);
    }

    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(1);
    }

    listen(server_fd, 3);
    std::cout << "Listening for commands on port " << port << "...\n";

    while (running) {
        int client_socket = accept(server_fd, nullptr, nullptr);
        if (client_socket >= 0) {
            std::thread(handle_client, client_socket).detach();
        }
    }
}

int main() {
    signal(SIGINT, stop_flask);
    start_flask();

    std::cout << "Flask started. Press Ctrl+C to stop everything.\n";

    // Run TCP listener in background
    std::thread listener(start_listener, 6000);
    listener.detach();

    // Main loop (can later include monitoring, hardware logic, etc.)
    while (running) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    return 0;
}
