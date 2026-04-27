# Mapping of city names to airport IATA codes
CITY_TO_AIRPORTS = {
    "chicago": ["ORD", "MDW"],
    "los angeles": ["LAX", "LGB", "ONT", "BUR"],
    "new york": ["JFK", "LGA", "EWR"],
    "san francisco": ["SFO", "OAK", "SJC"],
    "boston": ["BOS", "MHT"],
    "denver": ["DEN"],
    "dallas": ["DFW", "DAL"],
    "houston": ["IAH", "HOU"],
    "miami": ["MIA", "FLL"],
    "atlanta": ["ATL"],
    "phoenix": ["PHX"],
    "seattle": ["SEA"],
    "washington dc": ["DCA", "IAD", "BWI"],
    "philadelphia": ["PHL"],
    "minneapolis": ["MSP"],
    "detroit": ["DTW"],
    "las vegas": ["LAS"],
    "san diego": ["SAN"],
    "orlando": ["MCO"],
    "charlotte": ["CLT"],
    "austin": ["AUS"],
    "portland": ["PDX"],
    "milwaukee": ["MKE"],
    "london": ["LHR", "LGW", "LCY", "STN", "LTN"],
    "paris": ["CDG", "ORY"],
    "tokyo": ["NRT", "HND"],
    "beijing": ["PEI", "PKX"],
    "hong kong": ["HKG"],
    "singapore": ["SIN"],
    "dubai": ["DXB"],
    "sydney": ["SYD"],
    "melbourne": ["MEL"],
    "toronto": ["YYZ", "YTZ"],
    "vancouver": ["YVR"],
    "mexico city": ["MEX"],
    "cancun": ["CUN"],
    "munich": ["MUC"],
    "amsterdam": ["AMS"],
    "frankfurt": ["FRA"],
    "zurich": ["ZRH"],
}

def expand_city_to_airports(location: str) -> list[str]:
    """
    Expand a city name to all airport IATA codes, or return the location if it's already an airport code.
    
    Args:
        location: City name (e.g., "Chicago") or airport code (e.g., "ORD")
    
    Returns:
        List of airport IATA codes
    """
    location_lower = location.lower().strip()
    
    # Check if it's a known city
    if location_lower in CITY_TO_AIRPORTS:
        return CITY_TO_AIRPORTS[location_lower]
    
    # Otherwise, assume it's already an airport code
    return [location.upper()]

