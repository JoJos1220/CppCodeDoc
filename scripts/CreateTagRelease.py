# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html


"""
Automatically create TAG and Release it on github.
In combination, a Discussion is created and wiki file is updated.
"""

import os
import sys
import re
import subprocess
import tempfile
import getpass
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.app_info import (__version__, __author__)

# ======= Configuration ==========
# Repository-Owner (GitHub-Username)
OWNER = f"{__author__}"
# Repository-Name
REPO = "CppCodeDoc"
# Discussion-Categorie (shown discussion categorie in Github)
CATEGORY_NAME = "General"
# Discussion title
TITLE = "Release of CppCodeDoc Version " + __version__
# Discussion appendix
INSTALLER_PATH = f".\installer\CppCodeDoc_{__version__}_Installer.exe"
# ================================

def update_wiki_from_help(github_token, repo_owner, repo_name, help_md_path, tag_name):
    """
    Updating Github Wiki with the content of help.md file - if available
    """
    wiki_repo_url = f"https://{github_token}@github.com/{repo_owner}/{repo_name}.wiki.git"
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            print("Cloning wiki repo...")
            subprocess.run(["git", "clone", wiki_repo_url, tmpdir], check=True, shell=False)

            wiki_home_path = os.path.join(tmpdir, "Home.md")

            print(f"Copying {help_md_path} to {wiki_home_path}...")
            with open(help_md_path, "r", encoding="utf-8") as src_file:
                content = src_file.read()
            with open(wiki_home_path, "w", encoding="utf-8") as dest_file:
                dest_file.write(content)

            print("Adding changes...")
            subprocess.run(["git", "add", "Home.md"], cwd=tmpdir,
                           check=True, shell=False)

            print("Committing changes...")
            subprocess.run(["git", "commit", "-m",
                            f"Update help file on release {tag_name}"],
                            cwd=tmpdir, check=True, shell=False)

            print("Pushing changes...")
            subprocess.run(["git", "push"], cwd=tmpdir, check=True, shell=False)

            print("Wiki updated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to update wiki. "
                  f"This will not stop the release process.\nDetails: {e}")
        except Exception as e:
            print(f"⚠️ Warning: Unexpected error while updating wiki: {e}")


def create_tag(version):
    """
    Create a Git tag for the release and push it to the remote repository.
    This function assumes that the current working directory is a Git repository.
    """

    if not re.fullmatch(r'[\w.\-/]+', version):
        raise ValueError(f"Invalid git tag name: {version}")

    try:
        subprocess.run(['git', 'tag', version], check=True, shell=False)
        print(f"Tag {version} created local.")
        subprocess.run(['git', 'push', 'origin', version], check=True, shell=False)
        print(f"Tag {version} pushed to remote repository.")
    except subprocess.CalledProcessError as e:
        print(f"Error during creation or pushing of TAG-Release: {e}")

def create_github_release(version, github_token, exe_path):
    """
    Create a GitHub release and upload the EXE file as an asset.
    This function requires the GitHub token to authenticate API requests.
    """

    # 1. Creation of Github Release
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }

    discussions_url = f"https://github.com/{OWNER}/{REPO}/discussions/categories/general"
    wiki_url = f"https://github.com/{OWNER}/{REPO}/wiki"
    issues_url = f"https://github.com/{OWNER}/{REPO}/issues"
    latest_release_url = f"https://github.com/{OWNER}/{REPO}/releases/latest"

    body_text = f"""
<img src="img/Banner_CppCodeDoc.png" alt="Banner" height="150" />

🚀 **CppCodeDoc Version {version} Released!**

---

## 🔄 Upgrade Instructions

- Close CppCodeDoc before starting the update.
- Backup your important configuration files before proceeding.

### If you use the Installer:
- Run the new installer with admin permissions and follow the prompts.
- After installation, restart the application as usual.

### If you update via Git repository:
- Pull the latest changes with `git pull` or reclone the repository.
- Run the GUI version with:  
  `python CppCodeDoc.py`  
- Or run the CLI version with:  
  `python CppCodeDoc.py --NoGui`  

---

## 📚 Useful Links
[![Documentation](https://img.shields.io/badge/-Documentation-blue?style=for-the-badge&logo=read-the-docs)]({wiki_url})
[![Issues](https://img.shields.io/badge/-Issue_Tracker-orange?style=for-the-badge&logo=github)]({issues_url})
[![Download](https://img.shields.io/badge/-Latest_Release-green?style=for-the-badge&logo=github)]({latest_release_url})
[![Discussions](https://img.shields.io/badge/-Discussions-purple?style=for-the-badge&logo=github)]({discussions_url})
---

🙏 Thanks to all contributors and supporters! 💙
"""

    data = {
        "tag_name": version,
        "name": f"Release {version}",
        "body": body_text,
        "draft": False,
        "prerelease": False
    }

    response = requests.post(url, headers=headers, json=data, timeout=10)
    if response.status_code != 201:
        print(f"❌ Error on creating GitHub release: {response.status_code} – {response.text}")
        return

    print(f"✅ GitHub release {version} successfully created.")
    release_id = response.json()["id"]
    print(f"GitHub release-id: {release_id}")

    # 2. Upload EXE-file as asset
    upload_url = response.json()["upload_url"].split("{")[0]
    file_name = os.path.basename(exe_path)

    with open(exe_path, "rb") as f:
        upload_headers = {
            "Authorization": f"token {github_token}",
            "Content-Type": "application/octet-stream"
        }
        upload_response = requests.post(
            f"{upload_url}?name={file_name}",
            headers=upload_headers,
            data=f,
            timeout=10
        )

    if upload_response.status_code == 201:
        print(f"✅ File '{file_name}' successfully uploaded to release.")
    else:
        print(f"❌ Error uploading asset: {upload_response.status_code} – {upload_response.text}")

def extract_changelog_for_version(version, changelog_path="changelog.md"):
    """
    extracts the changelog section for a specific version from the changelog.md file.
    """
    with open(changelog_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_line, end_line = None, None

    for i, line in enumerate(lines):
        if line.strip().lower().startswith(f"# changelog for version {version}".lower()):
            start_line = i
        elif start_line is not None and line.strip().lower().startswith("# changelog for version"):
            end_line = i
            break

    if start_line is None:
        raise ValueError(f"Version {version} not found in changelog.")
    end_line = end_line or len(lines)
    changelog_section = lines[start_line+1:end_line]
    return "".join(changelog_section).strip()

def format_changelog_md(changelog_text: str) -> str:
    """
    Formats the changelog text for better readability in Markdown.
        - Adds emojis to section headers.
    """
    lines = changelog_text.strip().splitlines()
    formatted = []
    section_icons = {
        "features": "✨",
        "bug fixes": "🐛",
        "changes": "🔧",
        "performance": "⚡",
        "documentation": "📝",
    }

    for line in lines:
        line = line.strip()
        if line.lower().startswith("###"):
            section = line[3:].strip()
            emoji = next((icon for name, icon in section_icons.items()
                          if name in section.lower()), "🗂")
            formatted.append(f"### {emoji} {section}")
        elif line.startswith("*"):
            formatted.append("- " + line[1:].strip().capitalize())
        else:
            formatted.append(line)

    return "\n".join(formatted)

def run_query(query, github_token, variables=None):
    """
    Runs a GraphQL query against the GitHub API.
    Returns the JSON response of the API-Request if successful.
    """
    api_url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url,
                             json={"query": query, "variables": variables or {}},
                             headers=headers, timeout=10)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"Query failed with code {response.status_code}: {response.text}")
    return response.json()

def get_repository_id(owner, name, github_token):
    """
    Retrieves the repository ID for a given owner and repository name.
    Uses the GitHub GraphQL
    """
    query = """
    query ($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
      }
    }
    """
    result = run_query(query, github_token, {"owner": owner, "name": name})
    return result["data"]["repository"]["id"]

def get_category_id(owner, name, github_token, category_name):
    """
    Retrieves the discussion category ID for a given owner, repository name, and category name.
    """
    query = """
    query ($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        discussionCategories(first: 10) {
          nodes {
            id
            name
          }
        }
      }
    }
    """
    result = run_query(query, github_token, {"owner": owner, "name": name})
    categories = result["data"]["repository"]["discussionCategories"]["nodes"]
    for category in categories:
        if category["name"].lower() == category_name.lower():
            return category["id"]
    raise ValueError(f"Category '{category_name}' not found.")

def create_discussion(repo_id, category_id, github_token, title, body):
    """
    Creates a discussion in the specified repository and category.
    Returns the URL of the created discussion.
    """
    query = """
    mutation ($repoId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {
        repositoryId: $repoId,
        categoryId: $categoryId,
        title: $title,
        body: $body
      }) {
        discussion {
          url
        }
      }
    }
    """
    result = run_query(query, github_token, {
        "repoId": repo_id,
        "categoryId": category_id,
        "title": title,
        "body": body
    })
    return result["data"]["createDiscussion"]["discussion"]["url"]


if __name__ == "__main__":


    """
    Main Script.
    Ensure that in previous step, the "Convert_PyToExe.py" script was run to create the installer.
    This script will create a Git tag, a GitHub release, and a discussion for the release.
    It will also update the GitHub wiki with the content of help.md if available.
    """
    if not os.path.isfile(INSTALLER_PATH):
        print(f"❌ Installer file not found: {INSTALLER_PATH}")
        print("➡️  Please build the installer before running this release script.")
        exit(1)

    github_token = getpass.getpass("🔑 Enter GitHub Classic-Token: ")
    # update wiki from help.md bevor creating tag
    update_wiki_from_help(github_token, OWNER, REPO, "./help.md", __version__)

    # creation of tag release
    create_tag(__version__)

    # creat github tag release
    create_github_release(__version__, github_token, INSTALLER_PATH)

    # creat github discussion
    try:
        print("Get Repository-ID ...")
        repo_id = get_repository_id(OWNER, REPO, github_token)
        print("Get Category-ID ...")
        category_id = get_category_id(OWNER, REPO, github_token, CATEGORY_NAME)
        print("Create Discussion ...")
        try:
            changelog_text = extract_changelog_for_version(__version__)
            changelog_text = format_changelog_md(changelog_text)
        except Exception as e:
            changelog_text = "*No changelog entry found.*"
            print(f"⚠️ {e}")

        release_url = f"https://github.com/{OWNER}/{REPO}/releases/tag/{__version__}"

        BODY = (
        f"🚀 We're excited to announce the release of **CppCodeDoc** version {__version__}!\n\n"
        f"## 🆕 Changelog\n\n"
        f"{changelog_text}\n\n"
        f"Thanks to everyone contributing, using, and supporting this project! 💙\n\n"
        f"[![Release](https://img.shields.io/badge/release-v{__version__}-brightgreen)]({release_url})"
        )

        url = create_discussion(repo_id, category_id, github_token, TITLE, BODY)
        print("✅ Discussion created:", url)
    except Exception as e:
        print("❌ ERROR:", e)
