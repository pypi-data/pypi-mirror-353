#!/usr/bin/env python3
"""
Git2WP - A command-line tool for publishing Git repository changes to WordPress.
"""
import os
import sys
import json
import click
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory or home config
env_path = Path.home() / ".config" / "git2wp" / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Configuration
CONFIG = {
    'wordpress_url': os.getenv('WORDPRESS_URL', ''),
    'wordpress_username': os.getenv('WORDPRESS_USERNAME', ''),
    'wordpress_password': os.getenv('WORDPRESS_PASSWORD', ''),
    'wordpress_token': os.getenv('WORDPRESS_TOKEN', ''),
    'git_path': os.getenv('GIT_PATH', str(Path.home() / 'github')),
}

# Colors for console output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def is_git_repo(path: str) -> bool:
    """Check if a path is a Git repository."""
    try:
        result = subprocess.run(
            ['git', '-C', path, 'rev-parse', '--is-inside-work-tree'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode().strip() == 'true'
    except subprocess.CalledProcessError:
        return False

def get_commit_info(repo_path: str, commit_hash: str = 'HEAD') -> Dict[str, Any]:
    """Get information about a specific commit."""
    try:
        # Get commit details
        result = subprocess.run(
            ['git', '-C', repo_path, 'show', '--no-patch', 
             '--format={"hash":"%H","short_hash":"%h","author":"%an","email":"%ae","date":"%ad","subject":"%s","body":"%b"}',
             commit_hash],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        commit_info = json.loads(result.stdout.decode())
        
        # Get changed files
        result = subprocess.run(
            ['git', '-C', repo_path, 'diff', '--name-status', f'{commit_hash}^..{commit_hash}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        changed_files = [line.split('\t') for line in result.stdout.decode().splitlines()]
        
        commit_info['changed_files'] = [
            {'status': status, 'path': path} 
            for status, path in changed_files if path
        ]
        
        return commit_info
        
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"{Colors.RED}Error getting commit info: {e}{Colors.END}", file=sys.stderr)
        sys.exit(1)

def test_wordpress_connection() -> bool:
    """Test connection to WordPress."""
    import requests
    from requests.auth import HTTPBasicAuth
    
    if not CONFIG['wordpress_url']:
        print(f"{Colors.YELLOW}WordPress URL not configured{Colors.END}")
        return False
    
    try:
        auth = None
        if CONFIG['wordpress_token']:
            headers = {'Authorization': f'Bearer {CONFIG["wordpress_token"]}'}
        elif CONFIG['wordpress_username'] and CONFIG['wordpress_password']:
            auth = HTTPBasicAuth(CONFIG['wordpress_username'], CONFIG['wordpress_password'])
            headers = {}
        else:
            print(f"{Colors.YELLOW}No WordPress authentication configured{Colors.END}")
            return False
            
        response = requests.get(
            f"{CONFIG['wordpress_url']}/wp-json",
            auth=auth,
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"{Colors.RED}Error connecting to WordPress: {e}{Colors.END}")
        return False

def publish_to_wordpress(title: str, content: str, status: str = 'draft') -> bool:
    """Publish content to WordPress."""
    import requests
    from requests.auth import HTTPBasicAuth
    
    try:
        auth = None
        if CONFIG['wordpress_token']:
            headers = {'Authorization': f'Bearer {CONFIG["wordpress_token"]}'}
        elif CONFIG['wordpress_username'] and CONFIG['wordpress_password']:
            auth = HTTPBasicAuth(CONFIG['wordpress_username'], CONFIG['wordpress_password'])
            headers = {}
        else:
            print(f"{Colors.RED}No WordPress authentication configured{Colors.END}")
            return False
            
        data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        response = requests.post(
            f"{CONFIG['wordpress_url']}/wp-json/wp/v2/posts",
            json=data,
            auth=auth,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            post = response.json()
            print(f"{Colors.GREEN}✓ Successfully published to WordPress!{Colors.END}")
            print(f"Post URL: {post.get('link', 'Unknown')}")
            return True
        else:
            print(f"{Colors.RED}Failed to publish to WordPress: {response.text}{Colors.END}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}Error publishing to WordPress: {e}{Colors.END}")
        return False

def format_commit_for_wordpress(repo_name: str, commit_info: Dict[str, Any]) -> str:
    """Format Git commit information for WordPress."""
    content = f"""<h2>Commit Details</h2>
    <p><strong>Repository:</strong> {repo_name}</p>
    <p><strong>Commit:</strong> <code>{commit_info['short_hash']}</code></p>
    <p><strong>Author:</strong> {commit_info['author']} &lt;{commit_info['email']}&gt;</p>
    <p><strong>Date:</strong> {commit_info['date']}</p>
    <h3>Message</h3>
    <p>{commit_info['subject']}</p>
    """
    
    if commit_info.get('body'):
        content += f"<pre>{commit_info['body']}</pre>"
    
    if commit_info.get('changed_files'):
        content += "<h3>Changed Files</h3><ul>"
        for file in commit_info['changed_files']:
            status = file['status']
            status_color = {
                'A': 'green',
                'M': 'yellow',
                'D': 'red',
                'R': 'blue',
                'C': 'cyan',
                'U': 'magenta'
            }.get(status[0], 'gray')
            content += f"<li><span style='color: {status_color}'>{status}</span> {file['path']}</li>"
        content += "</ul>"
    
    return content

@click.group()
@click.version_option(version='0.1.0')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """Git2WP - Publish Git repository changes to WordPress."""
    if verbose:
        print("Verbose mode enabled")

@cli.command()
@click.argument('repo_path', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--commit', '-c', default='HEAD', help='Commit hash to publish (default: HEAD)')
@click.option('--dry-run', is_flag=True, help='Show what would be published without making changes')
@click.option('--status', type=click.Choice(['draft', 'publish', 'pending', 'private']), 
              default='draft', help='Status for the WordPress post')
def publish(repo_path: str, commit: str, dry_run: bool, status: str):
    """Publish Git repository changes to WordPress."""
    # Validate repository
    if not is_git_repo(repo_path):
        print(f"{Colors.RED}Error: Not a Git repository: {repo_path}{Colors.END}", file=sys.stderr)
        sys.exit(1)
    
    # Get commit information
    print(f"{Colors.BLUE}Fetching commit information...{Colors.END}")
    commit_info = get_commit_info(repo_path, commit)
    
    # Print commit information
    print(f"\n{Colors.YELLOW}=== Commit Information ==={Colors.END}")
    print(f"{Colors.BLUE}Repository:{Colors.END} {os.path.basename(os.path.abspath(repo_path))}")
    print(f"{Colors.BLUE}Commit:{Colors.END} {commit_info['short_hash']} ({commit_info['hash']})")
    print(f"{Colors.BLUE}Author:{Colors.END} {commit_info['author']} <{commit_info['email']}>")
    print(f"{Colors.BLUE}Date:{Colors.END} {commit_info['date']}")
    print(f"{Colors.BLUE}Subject:{Colors.END} {commit_info['subject']}")
    
    if commit_info.get('changed_files'):
        print(f"\n{Colors.YELLOW}=== Changed Files ==={Colors.END}")
        for file in commit_info['changed_files']:
            status = file['status']
            status_color = {
                'A': Colors.GREEN,
                'M': Colors.YELLOW,
                'D': Colors.RED,
                'R': Colors.BLUE,
                'C': Colors.BLUE,
                'U': Colors.BLUE
            }.get(status[0], Colors.END)
            print(f"{status_color}{status}{Colors.END} {file['path']}")
    
    # Format content for WordPress
    repo_name = os.path.basename(os.path.abspath(repo_path))
    post_title = f"{repo_name}: {commit_info['subject']}"
    post_content = format_commit_for_wordpress(repo_name, commit_info)
    
    if dry_run:
        print(f"\n{Colors.YELLOW}=== Dry Run ==={Colors.END}")
        print(f"{Colors.BLUE}Would publish to WordPress with status: {status}{Colors.END}")
        print(f"{Colors.BLUE}Title:{Colors.END} {post_title}")
        print(f"{Colors.BLUE}Content Preview:{Colors.END}")
        print("-" * 80)
        print(post_content[:500] + ("..." if len(post_content) > 500 else ""))
        print("-" * 80)
        return
    
    # Publish to WordPress
    print(f"\n{Colors.YELLOW}=== Publishing to WordPress ==={Colors.END}")
    success = publish_to_wordpress(post_title, post_content, status)
    
    if not success:
        sys.exit(1)

@cli.command()
def test_connection():
    """Test connection to WordPress."""
    print(f"{Colors.BLUE}Testing WordPress connection...{Colors.END}")
    if test_wordpress_connection():
        print(f"{Colors.GREEN}✓ Successfully connected to WordPress!{Colors.END}")
    else:
        print(f"{Colors.RED}✗ Could not connect to WordPress.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
