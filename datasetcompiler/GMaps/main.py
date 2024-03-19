import request_agent

cities = [
    "Tokyo", "Jakarta", "Delhi", "Guangzhou", "Mumbai", "Manila", "Shanghai", "Sao Paulo", "Seoul",
    "Paris", "Bangkok", "London", "Dubai", "New York City", "Istanbul", "Kuala Lumpur", "Hong Kong", 
    "Singapore", "Rome", "Antalya", "Phuket", "Mecca", "Pattaya", "Taipei", "Miami", "Barcelona", 
    "Los Angeles", "Osaka", "Amsterdam", "Milan", "Vienna", "Venice", "Prague", "Madrid", "Dublin", 
    "Munich", "Toronto", "Berlin", "Ho Chi Minh City", "Orlando", "Florence", "St. Petersburg", "Sydney", 
    "Kyoto", "Las Vegas", "Moscow", "Athens", "Beijing", "San Francisco", "Mexico City", "Cairo", "Lima", 
    "Cape Town", "Buenos Aires", "Lisbon", "Budapest", "Brussels", "Warsaw", "Doha", 
    "Helsinki", "Oslo", "Stockholm", "Copenhagen", "Nairobi", "Bogota", "Rio de Janeiro", "Lahore", 
    "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata", "Casablanca", "Tel Aviv", "Jerusalem", 
    "Izmir", "Baku", "Tbilisi", "Yerevan", "Kathmandu", "Hanoi", "Yangon", "Colombo", 
    "Dhaka", "Tehran", "Baghdad", "Riyadh", "Amman", "Beirut", "Kuwait City", "Muscat", 
    "Dammam", "Abu Dhabi", "Sharjah", "Bengaluru", "Chiang Mai", "Hoi An", "Siem Reap", "Vientiane", 
    "Phnom Penh", "Luang Prabang", "Ulaanbaatar", "Astana", "Almaty", "Tashkent", "Samarkand", 
    "Bishkek", "Dushanbe", "Ashgabat", "Sofia", "Belgrade", "Sarajevo", "Zagreb", "Skopje", 
    "Ljubljana", "Tirana", "Podgorica", "Prishtina", "Riga", "Tallinn", "Vilnius", "Minsk", 
    "Chisinau", "Bucharest", "Bratislava", "Krakow", "Gdansk", "Wroclaw", "Poznan", "Zurich", 
    "Geneva", "Luxembourg", "Monaco", "San Marino", "Malta", "Reykjavik", 
    "Auckland", "Wellington", "Melbourne", "Perth", "Adelaide", 
    "Canberra", "Darwin", "Christchurch", "Suva", "Noumea", "Port Moresby", "Nadi", 
    "Apia", "Papeete", "Nuku'alofa", "Honiara", "Tarawa", 
    "Funafuti", "Maputo", "Luanda", "Accra", "Dakar", "Freetown", "Lagos", "Abuja", 
    "Cotonou", "Lomé"
]

types = [
    "museums",
    "sites",
    "street food",
    "restaurants",
    "shops",
    "architecture"
]

for city in cities:
    for type in types:
        request_agent.fetch_response(city, type)