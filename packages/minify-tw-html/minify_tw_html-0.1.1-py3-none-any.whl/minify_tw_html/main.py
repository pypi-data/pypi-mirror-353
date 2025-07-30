import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from prettyfmt import fmt_size_dual

log = logging.getLogger(__name__)


class BuildError(RuntimeError):
    """Raised if any step in the build fails."""


def get_js_dir():
    """Get the JavaScript directory containing package.json and ensure npm packages are installed."""
    js_dir = Path(__file__).parent / "javascript"
    package_json = js_dir / "package.json"
    node_modules = js_dir / "node_modules"

    if not package_json.exists():
        raise BuildError(f"JavaScript package.json not found at {package_json}")

    # Install npm packages if not already installed
    if not node_modules.exists():
        npm_cmd = ["npm", "install"]
        log.info("Installing npm dependencies...")
        log.info(f"Running: {' '.join(npm_cmd)}")
        try:
            subprocess.run(
                npm_cmd,
                cwd=js_dir,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise BuildError(f"Failed to install npm dependencies:\n{e.stderr}") from e

    return js_dir


def minify_tw_html(src_html: Path, dest_html: Path, *, minify_html: bool = True):
    """
    Process HTML file with optional Tailwind CSS v4 compilation and minification.

    This function will:
    1. Check for Tailwind v4 CDN script tags and compile/inline CSS if found
    2. Optionally minify the entire HTML including inline CSS and JS

    Expected Tailwind v4 CDN script formats:
    - <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    - <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
    - Any script tag containing "@tailwindcss/browser"

    Args:
        src_html: Input HTML file
        dest_html: Output HTML file
        minify_html: Whether to minify the HTML output
    """
    # Get initial file size
    initial_size = src_html.stat().st_size

    html_text = src_html.read_text(encoding="utf8")

    # Pattern for Tailwind v4 CDN scripts
    cdn_pattern = r'<script[^>]*src=["\'][^"\']*@tailwindcss/browser[^"\']*["\'][^>]*></script>'

    tailwind_found = bool(re.search(cdn_pattern, html_text, re.I))

    if tailwind_found:
        log.info("Tailwind v4 CDN script detected - will compile and inline Tailwind CSS")

        if shutil.which("npx") is None:
            raise BuildError(
                "npx is not found. Install Node.js and npm first to compile Tailwind CSS."
            )

        js_dir = get_js_dir()

        # Compile Tailwind CSS v4
        tw_css = """@import "tailwindcss";"""

        # Create temp files in the js directory so imports can be resolved
        with tempfile.TemporaryDirectory(dir=js_dir) as tmpdir:
            tmp_path = Path(tmpdir)
            input_css = tmp_path / "input.css"
            input_css.write_text(tw_css, encoding="utf8")

            output_css = tmp_path / "tailwind.min.css"

            tailwind_cmd = [
                "npx",
                "@tailwindcss/cli",
                "-i",
                str(input_css),
                "-o",
                str(output_css),
                "--minify",
            ]
            log.info(f"Running: {' '.join(tailwind_cmd)}")
            try:
                result = subprocess.run(
                    tailwind_cmd,
                    cwd=js_dir,  # Run in the JavaScript directory with installed packages
                    check=True,
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    log.info(f"Tailwind output: {result.stdout}")
                if result.stderr:
                    log.info(f"Tailwind stderr: {result.stderr}")
            except subprocess.CalledProcessError as e:
                log.error(f"Tailwind command failed with exit code {e.returncode}")
                if e.stdout:
                    log.error(f"Tailwind stdout: {e.stdout}")
                if e.stderr:
                    log.error(f"Tailwind stderr: {e.stderr}")
                raise BuildError(f"Tailwind CSS v4 build failed:\n{e.stderr}") from e

            css_text = output_css.read_text(encoding="utf8")

        # Replace Tailwind CDN script with compiled CSS
        processed_html = re.sub(
            cdn_pattern, f"<style>{css_text}</style>", html_text, count=1, flags=re.I
        )

        log.info("Tailwind CSS v4 compiled and inlined successfully")
    else:
        log.info("No Tailwind v4 CDN script found - proceeding with standard HTML processing")
        processed_html = html_text

    # Minification step (works with or without Tailwind)
    if minify_html:
        log.info("Minifying HTML (including inline CSS and JS)...")

        js_dir = get_js_dir()

        # Write processed HTML to a temp file for html-minifier-terser
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, dir=js_dir
        ) as tmp_file:
            tmp_file.write(processed_html)
            tmp_html_path = tmp_file.name

        minifier_cmd = [
            "npx",
            "html-minifier-terser",
            "--collapse-whitespace",
            "--remove-comments",
            "--minify-css",
            "true",
            "--minify-js",
            "true",
            "-o",
            str(dest_html.absolute()),
            tmp_html_path,
        ]
        log.info(f"Running: {' '.join(minifier_cmd)}")
        try:
            result = subprocess.run(
                minifier_cmd,
                cwd=js_dir,  # Run in the JavaScript directory with installed packages
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                log.info(f"HTML minifier output: {result.stdout}")
            if result.stderr:
                log.info(f"HTML minifier stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            log.error(f"HTML minifier command failed with exit code {e.returncode}")
            if e.stdout:
                log.error(f"HTML minifier stdout: {e.stdout}")
            if e.stderr:
                log.error(f"HTML minifier stderr: {e.stderr}")
            raise BuildError(f"HTML minification failed:\n{e.stderr}") from e
        finally:
            # Clean up temp file
            Path(tmp_html_path).unlink(missing_ok=True)

        log.info(f"HTML minified and written to {dest_html}")
    else:
        dest_html.write_text(processed_html, encoding="utf8")
        log.info(f"HTML written to {dest_html} (no minification)")

    # Get final file size and print statistics
    final_size = dest_html.stat().st_size

    # Print concise summary
    actions: list[str] = []
    if tailwind_found:
        actions.append("Tailwind CSS compiled")
    if minify_html:
        actions.append("HTML minified")

    action_str = ", ".join(actions) if actions else "Processed"

    # Calculate percentage change
    pct_change = ((final_size - initial_size) / initial_size) * 100
    pct_str = f" ({pct_change:+.1f}%)"

    log.warning(
        f"{action_str}: {fmt_size_dual(initial_size)} → {fmt_size_dual(final_size)}{pct_str}"
    )
