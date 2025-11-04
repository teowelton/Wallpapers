import os
import yaml
import subprocess

categories_dict = {}
themes_dict = {}


def load_metadata():
    with open("wallpaper_metadata.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def generate_thumbnails():
    directories = ["unthemed", "catppuccin", "nord"]
    max_file_size = 1024 * 1024  # 1 MiB in bytes

    for directory in directories:
        if not os.path.exists(directory):
            continue

        # Recursively get all image files
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                    file_path = os.path.join(root, file)

                    # Create thumbnail path
                    thumbnail_dir = os.path.join("thumbnails", root)
                    os.makedirs(thumbnail_dir, exist_ok=True)

                    # Determine output format
                    if file.lower().endswith(".gif"):
                        thumbnail_path = os.path.join(thumbnail_dir, file)
                    else:
                        # Change extension to .jpg
                        base_name = os.path.splitext(file)[0]
                        thumbnail_path = os.path.join(thumbnail_dir, base_name + ".jpg")

                    # Get original dimensions
                    try:
                        result = subprocess.run(
                            ["magick", "identify", "-format", "%w %h", file_path],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        width, height = map(int, result.stdout.strip().split())
                    except (subprocess.CalledProcessError, ValueError):
                        print(f"Error: Could not get dimensions for {file_path}")
                        continue

                    # Start with original dimensions and reduce until file size is acceptable
                    current_width, current_height = width, height
                    scale_factor = 0.9  # Reduce by 10% each iteration

                    while current_width > 1 and current_height > 1:
                        try:
                            # Create temporary file to test size
                            temp_path = thumbnail_path

                            # Resize image with quality setting (works for all formats)
                            subprocess.run(
                                [
                                    "magick",
                                    file_path,
                                    "-resize",
                                    f"{int(current_width)}x{int(current_height)}",
                                    "-quality",
                                    "95",
                                    thumbnail_path,
                                ],
                                check=True,
                                capture_output=True,
                            )

                            # Check file size
                            if os.path.getsize(thumbnail_path) <= max_file_size:
                                # File size is acceptable
                                print(
                                    f"Generated thumbnail {thumbnail_path} with file size {os.path.getsize(thumbnail_path) / 1024:.2f} KiB"
                                )
                                break
                            else:
                                # File too large, reduce dimensions and try again
                                os.remove(thumbnail_path)
                                current_width *= scale_factor
                                current_height *= scale_factor

                        except subprocess.CalledProcessError as e:
                            print(f"Error processing {file_path}: {e}")
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            break
                    else:
                        print(
                            f"Warning: Could not reduce {file_path} to acceptable size"
                        )


def generate_wallpaper_entry(wallpaper):
    # Initialize empty content variable
    content = ""

    # Get wallpaper details
    file_path = wallpaper.get("path", "")  # File path
    file_name = os.path.splitext(os.path.basename(file_path))[0]  # File name

    # Thumbnail path generation
    base_name = os.path.splitext(file_path)[0]
    if file_path.lower().endswith(".gif"):
        thumbnail_path = f"./thumbnails/{base_name}.gif"
    else:
        thumbnail_path = f"./thumbnails/{base_name}.jpg"

    resolution = wallpaper.get("resolution", "")  # Resolution
    theme = wallpaper.get("theme")  # Theme
    categories = wallpaper.get("categories", [])  # Categories
    source = wallpaper.get("source", "")  # Source URL
    original_art = wallpaper.get(
        "original_artwork", ""
    )  # Original art path (if color shifted)
    # Artist information
    artist_info = wallpaper.get("artist", {})
    artist_name = artist_info.get("name", "") if artist_info else None  # Artist name
    profile_links = (
        artist_info.get("profile_links", {}) if artist_info else None
    )  # Profile links

    # Exit early if no file path is provided
    if not file_path or not file_path.strip():
        return ""

    # Generate markdown content
    # Heading
    display_name = file_name.replace("-", " - ").replace("_", " ")
    content += f"### {display_name}\n\n"

    # Insert image
    content += f"[![{file_name}]({thumbnail_path})]({file_path})\n"

    # Insert thumbnail warning
    content += f"> **Note:** The above image is a thumbnail and is not full resolution. The full version can be downloaded [here]({file_path}).\n"

    # Resolution entry
    if resolution and resolution.strip():
        content += f"- **Resolution:** {resolution}\n"

    # Theme entry
    if theme and theme.strip():
        entry = [
            file_path,
            display_name,
            f"#{file_name.lower().replace('-', '---').replace('_', '-')}",
        ]
        themes_dict[theme].append(entry)

        # Format theme as inline code tag
        content += f"- **Theme:** `{theme}`\n"

    # Categories entry
    if categories and len(categories) > 0:
        # Add this wallpaper to each category in the categories_dict
        entry = [
            file_path,
            display_name,
            f"#{file_name.lower().replace('-', '---').replace('_', '-')}",
        ]
        for category in categories:
            categories_dict[category].append(entry)

        # Format categories as inline code tags
        category_tags = " ".join([f"`{cat}`" for cat in categories])
        content += f"- **Categories:** {category_tags}\n"

    # Artist entry
    if artist_name and artist_name.strip():
        content += f"- **Artist:** {artist_name}\n"

        # Profile links entry
        if profile_links:
            # Collect all available profile links
            links = []

            # Website
            if profile_links.get("website", "").strip():
                links.append(f"[*Website*]({profile_links['website']})")

            # YouTube
            if profile_links.get("youtube", "").strip():
                links.append(f"[*YouTube*]({profile_links['youtube']})")

            # Twitter
            if profile_links.get("twitter", "").strip():
                links.append(f"[*Twitter*]({profile_links['twitter']})")

            # Instagram
            if profile_links.get("instagram", "").strip():
                links.append(f"[*Instagram*]({profile_links['instagram']})")

            # Reddit
            if profile_links.get("reddit", "").strip():
                links.append(f"[*Reddit*]({profile_links['reddit']})")

            # Art Station
            if profile_links.get("art_station", "").strip():
                links.append(f"[*ArtStation*]({profile_links['art_station']})")

            # Deviant Art
            if profile_links.get("deviant_art", "").strip():
                links.append(f"[*DeviantArt*]({profile_links['deviant_art']})")

            # Add profile links line if any links exist
            if links:
                content += f"\t- **Profile Links:** {' | '.join(links)}\n"
    # If no artist info and no original artwork
    elif not original_art or not original_art.strip():
        content += "- **Artist:** *Unknown, feel free to create an issue or open a pull request if you know!*\n"

    # Source entry
    if source and source.strip():
        from urllib.parse import urlparse

        parsed_url = urlparse(source)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        content += f"- **Source:** [{domain}]({source})\n"

    # Original art entry
    if original_art and original_art.strip():
        original_art_file_name = os.path.splitext(os.path.basename(original_art))[0]
        original_art_wallpaper_entry = (
            original_art_file_name.lower().replace("-", "---").replace("_", "-")
        )
        content += f"- *This wallpaper is a color-shifted version of [this original artwork](#{original_art_wallpaper_entry}). All artist details can be found at the original artwork.*\n"

    content += "\n---\n\n"
    return content


def generate_readme():
    # Load metadata and get lists.
    metadata = load_metadata()
    wallpapers = metadata.get("wallpapers", [])
    themes = metadata.get("themes", [])
    categories = metadata.get("categories", [])

    # Start building the base Readme content.
    readme_content = """# Wallpapers
My personal collection of wallpapers, with as many credited artists as possible, and ***NO AI ART***

---

> **This Readme is auto-generated from `wallpaper_metadata.yml`. You can view the generator code in `scripts/MarkdownGenerator.py`**
> - Feel free to use this script for your own wallpapers repo, but please provide credit!
> - If **any artist attribution is missing**, or **you suspect something to be AI generated**, either contribute to `wallpaper_metadata.yaml` with a pull request or open an issue.
> - If you want to contribute wallpapers, please open a pull request with the wallpaper file and metadata in `wallpaper_metadata.yaml`.

---

## Table of Contents
- [Browse by Categories](#categories)
- [Browse by Themes](#themes)
- [Browse All Wallpapers](#wallpapers-1)

"""

    # Initialize categories_dict with empty lists for each category
    for category in categories:
        categories_dict[category] = []

    # Initialize themes_dict with empty lists for each theme
    for theme in themes:
        themes_dict[theme] = []

    # Generate entries for each wallpaper and append to the Readme content.
    wallpapers_content = "## Wallpapers\n\n"
    for wallpaper in wallpapers:
        generated_entry = generate_wallpaper_entry(wallpaper)
        wallpapers_content += generated_entry

    # Generate category section
    category_content = "## Categories\n\n"
    for category, entries in categories_dict.items():
        if entries:  # Only include categories with entries
            category_content += f"<details><summary>{category}</summary>\n\n"
            category_content += "| Preview | Wallpaper |\n"
            category_content += "|---------|-----------|\n"
            for entry in entries:
                file_path, display_name, anchor_link = entry
                category_content += f"| ![{display_name}]({file_path}) | [{display_name} (Click for Details)]({anchor_link}) |\n"
            category_content += "\n</details>\n\n"

    # Generate themes section
    theme_content = "## Themes\n\n"
    for theme, entries in themes_dict.items():
        if entries:  # Only include themes with entries
            theme_content += f"<details><summary>{theme}</summary>\n\n"
            theme_content += "| Preview | Wallpaper |\n"
            theme_content += "|---------|-----------|\n"
            for entry in entries:
                file_path, display_name, anchor_link = entry
                theme_content += f"| ![{display_name}]({file_path}) | [{display_name} (Click for Details)]({anchor_link}) |\n"
            theme_content += "\n</details>\n\n"

    # Combine all sections into the final Readme content
    readme_content += category_content
    readme_content += theme_content
    readme_content += wallpapers_content

    # Write all content to the README.md file.
    with open("README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)


def check_missing():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("README.md not found.")
        return

    image_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                rel_path = os.path.join(root, file).replace("\\", "/")
                if rel_path.startswith("./"):
                    rel_path = rel_path[2:]
                image_files.append(rel_path)

    missing_files = []
    for image in image_files:
        if image not in readme_content:
            missing_files.append(image)

    if missing_files:
        print(f"Warn: Found {len(missing_files)} Files missing from README.md:")
        for file in missing_files:
            print(f"  - {file}")


if __name__ == "__main__":
    generate_thumbnails()
    generate_readme()
    check_missing()
