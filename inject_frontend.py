import os

files_to_inject = {
    "Frontend/create_trip_screen/code.html": "create_trip.js",
    "Frontend/my_trips_screen/code.html": "my_trips.js",
    "Frontend/itinerary_builder_screen/code.html": "itinerary.js"
}

def inject():
    for html_path, js_filename in files_to_inject.items():
        if not os.path.exists(html_path):
            print(f"Skipping {html_path}: File not found")
            continue
            
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if f'src="{js_filename}"' in content:
            print(f"Skipping {html_path}: Already injected")
            continue
            
        # Insert script tag before </body>
        script_tag = f'<script src="{js_filename}"></script>\n'
        new_content = content.replace("</body>", f"{script_tag}</body>")
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully injected {js_filename} into {html_path}")

if __name__ == "__main__":
    inject()
