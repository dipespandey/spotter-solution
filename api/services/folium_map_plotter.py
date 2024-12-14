import folium
from django.conf import settings
from api.services.base_services import MapPlotter


class FoliumMapPlotter(MapPlotter):

    def plot_map(self, data: list[dict]):
        start_point = data[0]
        map_route = folium.Map(
            location=[start_point["latitude"], start_point["longitude"]], zoom_start=6)

        # Add points and draw lines
        coordinates = []
        for point in data:
            lat = point["latitude"]
            lon = point["longitude"]
            coordinates.append((lat, lon))

            # Check if the point has address and name
            if "name" in point and "address" in point:
                popup_text = f"Fuelstation: {point['name']}<br>"
                f"Address: {point['address']}<br>"
                f"City: {point['city']}, State: {point['state']}<br>"
                f"Price: {point['price']}"
                marker_color = "red"  # Highlight points with additional details in red
            else:
                popup_text = f"Latitude: {lat}, Longitude: {lon}"
                marker_color = "blue"  # Default color for basic points

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=marker_color)
            ).add_to(map_route)

        # Draw the route
        folium.PolyLine(coordinates, color="blue", weight=2.5,
                        opacity=1).add_to(map_route)

        # Save the map to an HTML file
        map_route.save(settings.MAP_PLOT_FILE)
