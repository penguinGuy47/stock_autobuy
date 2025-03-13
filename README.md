<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Autotrade - Stock Automation</h1>
  <p>
    Autotrade is a powerful automation tool that streamlines stock trading across multiple brokerages through a single interface. It enables users to execute trades, see trading history, and automate routine transactions without switching between different trading platforms. With support for major brokers like Chase, Fidelity, and Schwab, Autotrade simplifies the trading experience while saving time through its task management and automation capabilities. 
  </p>

  <h2>Current Features</h2>
  <ul>
    <li>User-friendly UI</li>
    <li>Profiles</li>
    <li>Task management</li>
      <li>Dashboard
        <ul>
          <li>
            Transaction History
          </li>
          <li>
            Upcoming Splits (WIP)
          </li>
        </ul>
      </li>
    <li>Broker support:
      <ul>
        <li>Chase 🟢</li>
        <li>Fennel 🔵</li>
        <li>Fidelity 🟢</li>
        <li>Firstrade 🔴</li>
        <li>Public 🟢</li>
        <li>Robinhood 🔵</li>
        <li>Schwab 🟢</li>
        <li>Wells Fargo 🟢</li>
      </ul>
      <p><strong>Legend:</strong> 🟢 = Working, 🟡 = Experiencing Issues, 🔴 = Down, 🔵 = In progress</p>
    </li>
  </ul>

  <h2>Upcoming Updates</h2>
  <ul>
    <li>More brokerages</li>
    <li>Headless mode</li>
    <li>MacOS Support</li>
  </ul>

  <h2>Requirements</h2>
  <p>
    Before running Autotrade, install the required Python packages using the included <code>requirements.txt</code> file:
  </p>
  <pre><code>pip install -r requirements.txt</code></pre>
  <p>
    Make sure you have <a href="https://www.python.org/downloads/">Python</a> installed.
  </p>

  <h3>Additional Requirements for Fennel Integration</h3>
  <p>The Fennel broker integration requires the following additional components:</p>
  <ul>
    <li><strong>Appium Server</strong>:
      <ul>
        <li>Install Node.js and npm: <a href="https://nodejs.org/">Download here</a></li>
        <li>Install Appium: <code>npm install -g appium</code></li>
        <li>Install Appium driver: <code>appium driver install uiautomator2</code></li>
        <li>Start Appium server at <code>http://localhost:4723</code> before using Fennel integration</li>
      </ul>
    </li>
    <li><strong>Android Studio</strong>:
      <ul>
        <li><a href="https://developer.android.com/studio">Download and install Android Studio</a></li>
        <li>Set up Android SDK through Android Studio</li>
        <li>Configure environment variables:
          <ul>
            <li>Set <code>ANDROID_HOME</code> to your Android SDK location</li>
            <li>Add <code>%ANDROID_HOME%\platform-tools</code> to your PATH</li>
          </ul>
        </li>
      </ul>
    </li>
    <li><strong>Android Emulator</strong>:
      <ul>
        <li>Use Android Studio's AVD Manager to create an emulator</li>
        <li>The default configuration uses device name "emulator-5554" (use the command <code>adb devices</code> to ensure its running)</li>
        <li>Install the Fennel app on the emulator before running</li>
      </ul>
    </li>
  </ul>

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
      <strong>Run the application:</strong> Double-click <code>start.bat</code> to start
    </li>
    <li>
      Before starting a Fennel task, open up a terminal and run <code>appium --base-path=/wd/hub</code>
    </li>
  </ol>
</body>
</html>
