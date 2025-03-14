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
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Panchang Calendar</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .email-container {
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, #4ca1af, #2c3e50);
            padding: 20px;
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        .content {
            padding: 25px;
            color: #333;
        }
        .content h2 {
            text-align: center;
            color: #2c3e50;
            font-size: 22px;
        }
        .details {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .details p {
            margin: 8px 0;
            font-size: 16px;
        }
        .highlight {
            font-weight: bold;
            color: #2c3e50;
        }
        .panchang-section {
            background: linear-gradient(135deg, #ff9a9e, #fad0c4);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            color: #2c3e50;
        }
        .panchang-section h3 {
            text-align: center;
            font-size: 20px;
            margin-bottom: 10px;
        }
        .panchang-section ul {
            list-style-type: none;
            padding: 0;
        }
        .panchang-section li {
            padding: 8px 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            justify-content: space-between;
        }
        .panchang-section li:last-child {
            border-bottom: none;
        }
        .footer {
            text-align: center;
            padding: 15px;
            font-size: 14px;
            color: #555;
            background: #f1f1f1;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>

    <div class="email-container">
        <div class="header">
            🌞 Panchang Calendar - {{ calendar_data['English Date'] }}
        </div>
        
        <div class="content">
            <h2>✨ Today Event : {{ calendar_data['Event'] }}</h2>
            
            <div class="details">
                <p><span class="highlight">📜 Event Quote:</span> {{ data['quote']['tamil'] }}</p>
                <p><span class="highlight">📜 Event Quote:</span> {{ data['quote']['english'] }}</p>
            </div>
            
            <div class="details">
                <p><span class="highlight">🌞 Morning Wish:</span> {{ data['morning_wish'] }}</p>
            </div>

            <div class="details">
                <p><span class="highlight">📆 English Date:</span> {{ calendar_data['English Date'] }}</p>
                <p><span class="highlight">🗓️ Regional Date:</span> {{ calendar_data['Regional Date String'] }}</p>
                <p><span class="highlight">🌍 Event:</span> {{ calendar_data['Event'] }}</p>
            </div>

            {% if calendar_data['Panchang'] != 'N/A' %}
            <div class="panchang-section">
                <h3>🕉️ Panchang Details</h3>
                <ul>
                    {% for key, value in calendar_data['Panchang'].items() %}
                    <li>
                        <span class="highlight">{{ key }}</span>
                        <span>{{ value }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% else %}
            <p>No Panchang data available.</p>
            {% endif %}
        </div>

        <div class="footer">
            <p>📅 Stay connected with the cosmic energies & plan your day wisely!</p>
            <p>🔗 <a href="https://india-calendar.onrender.com/" style="color: #2c3e50; text-decoration: none; font-weight: bold;">Visit Our Calendar</a> | ✨ <a href="mailto:support@yourwebsite.com" style="color: #2c3e50; text-decoration: none; font-weight: bold;"></a></p>
            <p>© 2025 India Calendar. All rights reserved.</p>
        </div>
        
    </div>

</body>
</html>
"""