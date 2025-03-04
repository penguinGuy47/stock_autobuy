<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SARA - Stock And Retail Automation (in progress)</title>
</head>
<body>
  <h1>SARA - Stock And Retail Automation (in progress)</h1>
  <p>
    A program that can automatically buy/sell stocks and retail products in a streamlined fashion after getting input from the user.
  </p>

  <h2>Current Features</h2>
  <ul>
    <li>User-friendly UI</li>
    <li>Profiles</li>
    <li>Task management</li>
    <li>Real-time updates</li>
    <li>Broker support:
      <ul>
        <li>Fidelity</li>
        <li>Chase</li>
        <li>Schwab</li>
        <li>Firstrade</li>
        <li>Wells Fargo</li>
        <li>Public</li>
      </ul>
    </li>
  </ul>

  <h2>Upcoming Updates</h2>
  <ul>
    <li>More brokerages</li>
    <li>Headless mode</li>
  </ul>

  <h2>Requirements</h2>
  <p>
    Before running SARA, install the required Python packages using the included <code>requirements.txt</code> file:
  </p>
  <pre><code>pip install -r requirements.txt</code></pre>
  <p>
    Make sure you have <a href="https://www.python.org/downloads/">Python</a> installed.
  </p>

  <h2>To Run</h2>
  <ol>
    <li><strong>Download</strong> the project repository.</li>
    <li>
      <strong>Install dependencies:</strong> Navigate to the project directory and run:
      <br>
      <code>pip install -r requirements.txt</code>
    </li>
    <li>
      <strong>Configure the start script:</strong>
      <ul>
        <li>Right-click and edit the <code>start.bat</code> file.</li>
        <li>Change the path <code>"C:\Users\%USERNAME%\Desktop\Code\Python\autobuy"</code> to the directory where you downloaded the project.</li>
      </ul>
    </li>
    <li>
      <strong>Run the application:</strong> Double-click <code>start.bat</code> to start SARA.
    </li>
  </ol>
</body>
</html>
