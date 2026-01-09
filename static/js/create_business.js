let map;
let marker;

function initAutocomplete() {
    const input = document.getElementById('places-search');
    const autocomplete = new google.maps.places.Autocomplete(input, {
        types: ['establishment'],
        fields: ['name', 'formatted_address', 'geometry', 'place_id']
    });

    // Default location (center of map before user selects anything)
    const defaultLatLng = { lat: 51.5074, lng: -0.1278 }; // London

    // Initialize the map
    map = new google.maps.Map(document.getElementById('map'), {
        center: defaultLatLng,
        zoom: 14,
        mapTypeControl: false,
    });

    marker = new google.maps.Marker({
        map: map,
        position: defaultLatLng
    });

    autocomplete.addListener('place_changed', () => {
        const place = autocomplete.getPlace();

        if (!place.geometry || !place.name || !place.formatted_address || !place.place_id) {
            alert('Please select a valid business from the suggestions.');
            return;
        }

        // Update hidden inputs
        document.getElementById('business-name').value = place.name;
        document.getElementById('business-address').value = place.formatted_address;
        document.getElementById('google-url').value = `https://search.google.com/local/writereview?placeid=${place.place_id}`;

        // Update map position and marker
        map.setCenter(place.geometry.location);
        map.setZoom(16);

        marker.setPosition(place.geometry.location);
        marker.setTitle(place.name);
    });
}

window.onload = initAutocomplete;
