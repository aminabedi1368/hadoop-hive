import subprocess
import logging
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

# Configure logging
logging.basicConfig(level=logging.INFO)

# Hive connection details
hive_query = "SELECT * FROM trading_data"

# Fetch data from Hive
def fetch_data():
    try:
        result = subprocess.run(['hive', '-e', hive_query], stdout=subprocess.PIPE, text=True)
        raw_data = result.stdout.strip()
        logging.info("Fetched data successfully from Hive.")
        return raw_data
    except Exception as e:
        logging.error(f"Error fetching data from Hive: {e}")
        return None

# Process the fetched data
def process_data(raw_data):
    if raw_data:
        rows = raw_data.split('\n')
        # Assuming the first row is the actual data, not headers
        data = [row.split('\t') for row in rows if row]
        return data
    else:
        return []

# Calculate moving average
def calculate_moving_average(data, window_size):
    if len(data) < window_size:
        return []
    moving_averages = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        moving_average = sum(window) / window_size
        moving_averages.append(moving_average)
    return moving_averages

# Generate HTML
def generate_html(dates, vwap, rsi, ma):
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trading Indicators</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>

        <h1>Trading Indicators</h1>

        <canvas id="vwapChart" width="400" height="200"></canvas>
        <canvas id="rsiChart" width="400" height="200"></canvas>
        <canvas id="maChart" width="400" height="200"></canvas>

        <script>
            var dates = {json.dumps(dates)};
            var vwap = {json.dumps(vwap)};
            var rsi = {json.dumps(rsi)};
            var ma = {json.dumps(ma)};

            // VWAP Chart
            var ctx = document.getElementById('vwapChart').getContext('2d');
            var vwapChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dates,
                    datasets: [{{
                        label: 'VWAP',
                        data: vwap,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        fill: false
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // RSI Chart
            var ctx2 = document.getElementById('rsiChart').getContext('2d');
            var rsiChart = new Chart(ctx2, {{
                type: 'line',
                data: {{
                    labels: dates,
                    datasets: [{{
                        label: 'RSI',
                        data: rsi,
                        borderColor: 'rgba(153, 102, 255, 1)',
                        fill: false
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            // MA Chart
            var ctx3 = document.getElementById('maChart').getContext('2d');
            var maChart = new Chart(ctx3, {{
                type: 'line',
                data: {{
                    labels: dates.slice({len(dates) - len(ma)}),
                    datasets: [{{
                        label: 'Moving Average',
                        data: ma,
                        borderColor: 'rgba(255, 159, 64, 1)',
                        fill: false
                    }}]
                }},
                options: {{
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>

    </body>
    </html>
    """
    return html

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        raw_data = fetch_data()
        data = process_data(raw_data)

        # Prepare data for the charts
        if data:
            # Assuming the first column is 'date', the second column is 'vwap', and the third column is 'rsi'
            dates = [row[0] for row in data]
            vwap = [float(row[2]) for row in data]  # Ensure conversion to float
            rsi = [float(row[3]) for row in data]   # Ensure conversion to float
            
            # Calculate moving average with a window size of 5
            window_size = 5
            ma = calculate_moving_average(vwap, window_size)

            # Generate HTML
            html_content = generate_html(dates, vwap, rsi, ma)

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
        else:
            logging.error("No data to process.")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"No data to process.")

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = ('', 5000)  # Set the port to 5000
    httpd = server_class(server_address, handler_class)
    logging.info("Starting server on port 5000...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

