#!/bin/bash
# .github/hooks/version-hook.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Path to your pyproject.toml file
PYPROJECT_PATH="pyproject.toml"
CHANGELOG_PATH="CHANGELOG.md"

# Extract current version from pyproject.toml
get_current_version() {
    # Completely rewritten version extraction
    # Use awk for more precise extraction
    VERSION=$(awk -F'"' '/^version = / {print $2}' "$PYPROJECT_PATH")
    echo "$VERSION"
}

# Check if version has changed compared to the remote branch
version_has_changed() {
    CURRENT_VERSION=$(get_current_version)
    CURRENT_BRANCH=$(git branch --show-current)
    
    echo "Detected current version: $CURRENT_VERSION"
    
    # Try to get the version from the remote repo
    if git ls-remote --exit-code origin &>/dev/null; then
        # Check if the remote branch exists
        if git show-ref --verify --quiet refs/remotes/origin/$CURRENT_BRANCH; then
            # Get the remote version from pyproject.toml
            REMOTE_VERSION=$(git show origin/$CURRENT_BRANCH:$PYPROJECT_PATH 2>/dev/null | 
                             awk -F'"' '/^version = / {print $2}' || echo "not-found")
            
            if [ "$REMOTE_VERSION" != "$CURRENT_VERSION" ]; then
                echo -e "${YELLOW}Version changed from $REMOTE_VERSION to $CURRENT_VERSION${NC}"
                return 0  # True - version has changed
            else
                echo -e "${BLUE}Version unchanged: $CURRENT_VERSION${NC}"
            fi
        else
            # New branch
            echo -e "${YELLOW}New branch or branch not yet pushed, using version: $CURRENT_VERSION${NC}"
            return 0
        fi
    else
        # If remote doesn't exist yet, consider this a new project
        echo -e "${YELLOW}Remote not found, assuming new project with version $CURRENT_VERSION${NC}"
        return 0  # True - new project
    fi
    
    return 1  # False - version hasn't changed
}

# Extract GitHub repository name from git remote
get_repo_info() {
    REMOTE_URL=$(git config --get remote.origin.url)
    if [[ $REMOTE_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
        OWNER="${BASH_REMATCH[1]}"
        REPO="${BASH_REMATCH[2]}"
        echo "$OWNER/$REPO"
    else
        echo ""
    fi
}

# Format commit message with PR and issue links
format_commit_message() {
    local MSG="$1"
    local REPO_INFO="$2"
    
    # Skip if no repo info
    if [ -z "$REPO_INFO" ]; then
        echo "$MSG"
        return
    fi
    
    # Extract PR number if present in commit message (PR #123)
    local PR_FORMATTED="$MSG"
    if [[ $MSG =~ Merge\ pull\ request\ #([0-9]+) ]]; then
        PR_NUM="${BASH_REMATCH[1]}"
        # Get the PR author using GitHub API if possible (requires curl and GitHub token)
        if command -v curl >/dev/null && [ -n "$GITHUB_TOKEN" ]; then
            PR_AUTHOR=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                "https://api.github.com/repos/$REPO_INFO/pulls/$PR_NUM" | 
                grep -o '"login": *"[^"]*"' | head -1 | sed 's/"login": *"\(.*\)"/\1/')
            
            if [ -n "$PR_AUTHOR" ]; then
                PR_FORMATTED="$MSG [PR #$PR_NUM by @$PR_AUTHOR]"
            else
                PR_FORMATTED="$MSG [PR #$PR_NUM]"
            fi
        else
            PR_FORMATTED="$MSG [PR #$PR_NUM]"
        fi
    elif [[ $MSG =~ \(#([0-9]+)\) ]]; then
        PR_NUM="${BASH_REMATCH[1]}"
        PR_FORMATTED="$MSG (PR #$PR_NUM)"
    fi
    
    # Extract issue numbers (fixes #123, closes #456, etc.)
    local ISSUES_FORMATTED="$PR_FORMATTED"
    local ISSUE_KEYWORDS="fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved"
    
    if [[ $PR_FORMATTED =~ ($ISSUE_KEYWORDS)[:space:]*#([0-9]+) ]]; then
        ISSUE_NUM="${BASH_REMATCH[2]}"
        ISSUES_FORMATTED="${PR_FORMATTED/\#$ISSUE_NUM/[#$ISSUE_NUM](https://github.com/$REPO_INFO/issues/$ISSUE_NUM)}"
    fi
    
    echo "$ISSUES_FORMATTED"
}

# Update the changelog file with the new version
update_changelog() {
    VERSION=$1
    DATE=$(date +"%Y-%m-%d")
    REPO_INFO=$(get_repo_info)
    
    # Create changelog if it doesn't exist
    if [ ! -f "$CHANGELOG_PATH" ]; then
        echo "# Changelog" > "$CHANGELOG_PATH"
        echo "" >> "$CHANGELOG_PATH"
        echo -e "${GREEN}Created new changelog file${NC}"
    fi
    
    # Get commits since the last version tag
    LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    
    if [ -z "$LAST_TAG" ]; then
        # If no tags exist, get all commits
        RAW_CHANGES=$(git log --pretty=format:"%s" | grep -v "Merge\|Update changelog\|Apply formatting" | head -15)
    else
        # Get commits since the last tag
        RAW_CHANGES=$(git log ${LAST_TAG}..HEAD --pretty=format:"%s" | grep -v "Merge\|Update changelog\|Apply formatting")
    fi
    
    # Format changes with PR and issue links
    CHANGES=""
    if [ -z "$RAW_CHANGES" ]; then
        CHANGES="- Minor updates and fixes"
    else
        while IFS= read -r line; do
            # Format each commit message
            FORMATTED_LINE=$(format_commit_message "$line" "$REPO_INFO")
            CHANGES="${CHANGES}- ${FORMATTED_LINE}\n"
        done <<< "$RAW_CHANGES"
    fi
    
    # Add new version section at the top of the changelog
    TMP_FILE=$(mktemp)
    echo "# Changelog" > "$TMP_FILE"
    echo "" >> "$TMP_FILE"
    echo "## [$VERSION] - $DATE" >> "$TMP_FILE"
    echo "" >> "$TMP_FILE"
    echo "### Changes" >> "$TMP_FILE"
    echo -e "$CHANGES" >> "$TMP_FILE"
    echo "" >> "$TMP_FILE"
    # If changelog exists and has content, append everything after the first line
    if [ -s "$CHANGELOG_PATH" ]; then
        tail -n +2 "$CHANGELOG_PATH" >> "$TMP_FILE"
    fi
    mv "$TMP_FILE" "$CHANGELOG_PATH"
    
    # Stage the changelog
    git add "$CHANGELOG_PATH"
    
    echo -e "${GREEN}Updated $CHANGELOG_PATH with changes for version $VERSION${NC}"
}

# Main execution
main() {
    if version_has_changed; then
        VERSION=$(get_current_version)
        
        # Debug output to verify correct version extraction
        echo "Version detected for tagging: '$VERSION'"
        
        # Update changelog and commit
        update_changelog "$VERSION"
        git commit -m "Update changelog for version $VERSION" || true
        
        # Create tag name - Fix: ensure the version is correctly formatted for a git tag
        TAG_VERSION="v$VERSION"
        
        # Debug output
        echo "Creating tag: '$TAG_VERSION'"
        
        # Tag the commit with the version
        git tag -a "$TAG_VERSION" -m "Version $VERSION"
        echo -e "${GREEN}Tagged commit with $TAG_VERSION${NC}"
        
        echo -e "${GREEN}All version update tasks completed successfully!${NC}"
    fi
}

# Run the main function
main