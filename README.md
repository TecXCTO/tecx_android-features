# tecx_android-features
TecX Android Features


To pull all the repositories from your GitHub account back down onto your device at once, we cannot download them by clicking through the web interface. Instead, we can use a native Linux command suite (gh - GitHub Official CLI) inside your terminal.
This tool authenticates your profile directly and completely downloads every single repository matching your username automatically.
Follow this exact sequence in your Termux Ubuntu container to pull your repositories down safely:
## Step 1: Install the GitHub CLI Utility
Run this command string to install the official GitHub management tool on your Ubuntu container:

sudo apt update && sudo apt install gh -y

## Step 2: Authenticate with Your GitHub Profile
Run the authorization script to link the terminal safely to your GitHub account:

gh auth login

Follow these precise configuration choices on your screen:

   1. What is your preferred protocol for Git operations? Choose HTTPS.
   2. Authenticate Git with your GitHub credentials? Choose Yes.
   3. How would you like to authenticate GitHub CLI? Choose Login with a web browser.
   4. The terminal will print a 8-character activation code (e.g., XXXX-XXXX). Copy it.
   5. Press Enter to open the browser window, or manually open [github.com](https://github.com/login/device) in your web browser, paste your activation code, and tap Authorize.

------------------------------
## Step 3: Automatically Download All Repositories
Once your terminal prints ✓ Logged in as TecXTO, run this automation loop command. It will read your profile listings and download every repository you own straight into a new directory:

# Create a fresh storage root directory on your phone
mkdir -p ~/recovered_repositories
cd ~/recovered_repositories
# Fetch and clone every repository registered under your account automatically
gh repo list --limit 1000 --json name -q '.[].name' | while read -r repo; do
  gh repo clone "$repo"done

## 📊 Verification Check
Once the download loop completes, verify your recovered projects by running:

ls -la ~/recovered_repositories/

You will see every repository matching your account listed as its own independent, restored folder ready for work.
Run the gh auth login block right now, and let me know if it registers your profile successfully!

