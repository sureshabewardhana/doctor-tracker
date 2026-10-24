from flask import Flask, jsonify, render_template_string
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import fetch_echannelling_data

app = Flask(__name__)

# Global variable එකක data සේව් කරගැනීම
latest_data = []

def run_scraper_job():
    global latest_data
    print("Running scheduled scraper job...")
    latest_data = fetch_echannelling_data()

# පැයකට සැරයක් Auto-Update වෙන Scheduler එක
scheduler = BackgroundScheduler()
scheduler.add_job(func=run_scraper_job, trigger="interval", hours=1)
scheduler.start()

# HTML Mobile Dashboard Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doctor Channeling Tracker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-slate-900 text-white font-sans min-h-screen p-4">
    <div class="max-w-md mx-auto">
        <header class="flex justify-between items-center mb-6 pt-2">
            <div>
                <h1 class="text-xl font-bold text-cyan-400">Channeling Tracker</h1>
                <p class="text-xs text-slate-400">eChannelling Daily Sync</p>
            </div>
            <button onclick="location.reload()" class="bg-cyan-600 hover:bg-cyan-500 p-2.5 rounded-xl text-sm font-semibold">
                <i class="fa-solid fa-rotate"></i>
            </button>
        </header>

        <div id="cards-container" class="space-y-4">
            <!-- Data Cards will be loaded here dynamically -->
            <div class="p-4 bg-slate-800 rounded-2xl border border-slate-700 animate-pulse">
                <div class="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-slate-700 rounded w-1/2"></div>
            </div>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                const container = document.getElementById('cards-container');
                
                if(!data || data.length === 0) {
                    container.innerHTML = '<p class="text-center text-slate-400">Fetching live data from eChannelling...</p>';
                    return;
                }

                container.innerHTML = data.map(doc => `
                    <div class="bg-slate-800 border border-slate-700/80 rounded-2xl p-4 shadow-lg">
                        <div class="flex justify-between items-start mb-3 border-b border-slate-700/50 pb-2">
                            <div>
                                <h3 class="font-bold text-base text-slate-100">${doc.doctor}</h3>
                                <p class="text-xs text-slate-400">${doc.timestamp}</p>
                            </div>
                            <span class="px-2 py-0.5 text-xs rounded-full bg-emerald-500/20 text-emerald-400 font-medium">
                                Active
                            </span>
                        </div>
                        <div class="space-y-2">
                            ${doc.sessions.map(s => `
                                <div class="bg-slate-900/60 p-3 rounded-xl flex justify-between items-center">
                                    <div>
                                        <p class="text-xs font-semibold text-slate-200">${s.hospital}</p>
                                        <p class="text-[10px] text-slate-400">Status: ${s.status}</p>
                                    </div>
                                    <div class="text-right">
                                        <span class="text-sm font-bold text-cyan-400">${s.booked}</span>
                                        <span class="text-xs text-slate-500">/${s.max}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
            }
        }

        loadData();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    global latest_data
    if not latest_data:
        # First-time fetch
        run_scraper_job()
    return jsonify(latest_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
