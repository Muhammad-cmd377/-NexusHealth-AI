from pyngrok import ngrok
import subprocess

process = subprocess.Popen(["streamlit", "run", "app.py"])
public_url = ngrok.connect(8501)
print(f"\n🌐 Public URL: {public_url}\n")
input("Press Enter to stop...")