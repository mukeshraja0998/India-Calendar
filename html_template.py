# HTML content template
html_template_1 = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panchang Calendar</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .navbar {
            background: linear-gradient(to right, #2c3e50, #4ca1af);
        }
        .navbar-brand, .nav-link {
            color: white !important;
            font-weight: bold;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            background: linear-gradient(to right, #ff9a9e, #fad0c4);
            color: #2c3e50;
        }
        .card-title {
            font-size: 1.5rem;
            font-weight: bold;
        }
        .list-group-item {
            background: transparent;
            border: none;
            font-size: 1.1rem;
        }
        .footer {
            background-color: #2c3e50;
            color: white;
            text-align: center;
            padding: 10px 0;
            margin-top: 30px;
        }
    </style>
</head>
<body>

<nav class="navbar navbar-expand-lg">
    <div class="container">
        <a class="navbar-brand" href="#">📅 Panchang Calendar</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                    <a class="nav-link" href="/home">🏠 Home</a>
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card p-4">
                <h2 class="card-title text-center mb-4">Panchang Details</h2>
                <div class="list-group">
                    <div class="list-group-item d-flex justify-content-between">
                        <strong>📆 English Date:</strong> <span>{{ data['English Date'] }}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between">
                        <strong>🗓️ {{ calendar_type }} Date:</strong> <span>{{ data['Regional Date String'] }}</span>
                    </div>
                    <div class="list-group-item d-flex justify-content-between">
                        <strong>🌍 {{ calendar_type }} Event:</strong> <span>{{ data['Event'] }}</span>
                    </div>
                </div>
                <hr>
                <h4 class="text-center mt-3">🕉️ Panchang Details</h4>
                <ul class="list-group">
                    {% for key, value in data['Panchang'].items() %}
                    <li class="list-group-item d-flex justify-content-between">
                        <strong>{{ key }}</strong> <span>{{ value }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="footer">
    <p>© 2025 Panchang Calendar | All Rights Reserved</p>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

html_template_2 = """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panchang Calendar</title>
        <!-- Bootstrap CSS -->
        <link
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
            rel="stylesheet">
        <style>
        body {
            background-color: #f8f9fa;
        }
        .navbar {
            background: linear-gradient(to right, #2c3e50, #4ca1af);
        }
        .navbar-brand, .nav-link {
            color: white !important;
            font-weight: bold;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            background: linear-gradient(to right, #ff9a9e, #fad0c4);
            color: #2c3e50;
        }
        .card-title {
            font-size: 1.5rem;
            font-weight: bold;
        }
        .list-group-item {
            background: transparent;
            border: none;
            font-size: 1.1rem;
        }
        .footer {
            color: rgb(84, 211, 45);
            text-align: center;
            padding: 10px 0;
            margin-top: 30px;
        }
    </style>
    </head>
    <body>

        <div class="container mt-4">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card p-4">
                        <h2 class="card-title text-center mb-4">Panchang
                            Details</h2>
                        <h3 class="text-center">✨ Event Details: {{ event
                            }}</h3>
                        <div class="list-group">
                            <div
                                class="list-group-item d-flex justify-content-between">
                                <strong>Quote: </strong> <span>{{
                                    data['quote']['tamil'] }}</span>                  
                            </div>
                            <div
                                class="list-group-item d-flex justify-content-between">
                                <strong>Quote: </strong> <span>{{
                                    data['quote']['english'] }}</span>
                            </div>
                        </div>
                        <hr>
                        <h4 class="text-center">🌞 Morning Wish</h4>
                        <div class="list-group">
                            <div
                                class="list-group-item d-flex justify-content-between">
                                <strong>Wish:</strong> <span>{{
                                    data['morning_wish'] }}</span>
                            </div>
                        </div>

                        <div class="list-group">
                            <div
                                class="list-group-item d-flex justify-content-between">
                                <strong>📆 English Date:</strong> <span>{{
                                    calendar_data['English Date'] }}</span>
                            </div>
                            <div
                                class="list-group-item d-flex justify-content-between">
                                <strong>🗓️ Regional Date:</strong> <span>{{
                                    calendar_data['Regional Date String']
                                    }}</span>
                            </div>
                            <div
                                class="list-group-item d-flex justify-content-between">
                                <strong>🌍 Event:</strong> <span>{{
                                    calendar_data['Event'] }}</span>
                            </div>
                        </div>
                        <hr>
                        <h4 class="text-center mt-3">🕉️ Panchang Details</h4>
                        {% if calendar_data['Panchang'] != 'N/A' %}
                        <ul class="list-group">
                            {% for key, value in
                            calendar_data['Panchang'].items() %}
                            <li
                                class="list-group-item d-flex justify-content-between">
                                <strong>{{ key }}</strong> <span>{{ value
                                    }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                        {% else %}
                        <p>No Panchang data available.</p>
                        {% endif %}

                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Made with ❤️ By Mukesh</p>
        </div>


        <!-- Bootstrap JS -->
        <script
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
</html>
"""