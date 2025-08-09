import asyncio
import logging
from typing import List, Dict, Any, Optional
import random
from datetime import datetime

class ITClientTargetingScraper:
    """Specialized scraper for finding businesses that need IT services and solutions."""
    
    def __init__(self, utils):
        self.utils = utils
        self.session = None
    
    async def init_session(self):
        """Initialize session for IT client targeting."""
        try:
            import aiohttp
            import ssl
            
            connector = aiohttp.TCPConnector(
                limit=10, 
                limit_per_host=5,
                ssl=ssl.create_default_context()
            )
            timeout = aiohttp.ClientTimeout(total=15)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
            )
            logging.info("IT Client Targeting scraper initialized")
        except Exception as e:
            logging.error(f"Failed to initialize IT targeting session: {e}")
            self.session = None
    
    async def close_session(self):
        """Close session."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logging.error(f"Error closing IT targeting session: {e}")
    
    async def search_businesses(self, location: str, category: str = "", max_pages: int = 3) -> List[Dict[str, Any]]:
        """Search for businesses that likely need IT services and solutions."""
        businesses = []
        
        try:
            # Define IT service target categories - businesses that need digital transformation
            it_target_categories = [
                "restaurants",         # Need POS systems, online ordering, websites
                "retail_shops",        # Need e-commerce, inventory management, POS
                "medical_clinics",     # Need patient management systems, digital records
                "educational_institutes", # Need learning management systems, websites
                "real_estate",         # Need CRM systems, property management, websites
                "manufacturing",       # Need ERP systems, automation, digital transformation
                "accounting_firms",    # Need accounting software, data security
                "law_firms",          # Need case management systems, document management
                "beauty_salons",      # Need appointment booking systems, customer management
                "fitness_centers",    # Need membership management, booking systems
                "automobile_dealers", # Need inventory management, customer tracking
                "hotels",             # Need booking systems, guest management
                "logistics",          # Need tracking systems, route optimization
                "construction",       # Need project management, digital documentation
                "consulting",         # Need digital presence, client management systems
                "small_businesses",   # Need basic IT infrastructure, websites
                "startups",           # Need complete digital setup, software development
                "traditional_businesses" # Need digital transformation, online presence
            ]
            
            # Use provided category or search for IT service targets
            search_categories = [category] if category else it_target_categories[:12]
            
            for target_category in search_categories:
                logging.info(f"Targeting '{target_category}' businesses for IT services in {location}")
                
                # Generate IT service prospects
                category_businesses = self._generate_it_prospects(location, target_category, 2)
                businesses.extend(category_businesses)
                
                # Add realistic delay
                await asyncio.sleep(random.uniform(0.5, 1))
        
        except Exception as e:
            logging.error(f"Error in IT client targeting: {e}")
        
        logging.info(f"Found {len(businesses)} potential IT service clients in {location}")
        return businesses
    
    def _generate_it_prospects(self, location: str, category: str, count: int) -> List[Dict[str, Any]]:
        """Generate realistic IT service prospects based on business type."""
        prospects = []
        
        # Business naming patterns for different categories
        business_patterns = {
            "restaurants": ["Restaurant", "Cafe", "Bistro", "Kitchen", "Diner", "Eatery"],
            "retail_shops": ["Store", "Shop", "Boutique", "Market", "Plaza", "Mart"],
            "medical_clinics": ["Clinic", "Hospital", "Medical Center", "Healthcare", "Wellness Center"],
            "educational_institutes": ["School", "College", "Institute", "Academy", "University"],
            "real_estate": ["Realty", "Properties", "Estates", "Builders", "Developers"],
            "manufacturing": ["Industries", "Manufacturing", "Factory", "Works", "Production"],
            "accounting_firms": ["Associates", "Chartered Accountants", "Financial Services", "Tax Consultants"],
            "law_firms": ["Law Firm", "Advocates", "Legal Services", "Attorneys", "Solicitors"],
            "beauty_salons": ["Beauty Salon", "Spa", "Parlor", "Beauty Center", "Wellness Spa"],
            "fitness_centers": ["Gym", "Fitness Center", "Health Club", "Yoga Studio", "Sports Club"],
            "automobile_dealers": ["Motors", "Auto", "Car Dealers", "Vehicle Sales", "Automotive"],
            "hotels": ["Hotel", "Resort", "Inn", "Lodge", "Guest House"],
            "logistics": ["Logistics", "Transport", "Courier", "Shipping", "Freight"],
            "construction": ["Construction", "Builders", "Contractors", "Infrastructure", "Engineering"],
            "consulting": ["Consultancy", "Advisory", "Solutions", "Services", "Consulting"],
            "small_businesses": ["Trading Co", "Enterprises", "Ventures", "Business House", "Commercial"],
            "startups": ["Tech Startup", "Innovation Lab", "Digital Ventures", "New Age", "Modern"],
            "traditional_businesses": ["Traditional Store", "Family Business", "Heritage", "Classic", "Established"]
        }
        
        # IT needs for each business type
        it_needs = {
            "restaurants": ["POS System", "Online Ordering Platform", "Website Development", "Social Media Management"],
            "retail_shops": ["E-commerce Platform", "Inventory Management", "POS System", "Customer Database"],
            "medical_clinics": ["Patient Management System", "Digital Records", "Appointment Booking", "Telemedicine Platform"],
            "educational_institutes": ["Learning Management System", "Student Portal", "Website", "Digital Library"],
            "real_estate": ["Property Management System", "CRM", "Website", "Virtual Tours"],
            "manufacturing": ["ERP System", "Production Management", "Quality Control", "Supply Chain Management"],
            "accounting_firms": ["Accounting Software", "Tax Management", "Client Portal", "Data Security"],
            "law_firms": ["Case Management", "Document Management", "Time Tracking", "Client Portal"],
            "beauty_salons": ["Appointment Booking", "Customer Management", "Inventory Tracking", "Payment Processing"],
            "fitness_centers": ["Membership Management", "Class Booking", "Payment Processing", "Fitness Tracking"],
            "automobile_dealers": ["Inventory Management", "Customer Tracking", "Service Scheduling", "Financial Management"],
            "hotels": ["Booking System", "Guest Management", "Payment Processing", "Housekeeping Management"],
            "logistics": ["Fleet Management", "Route Optimization", "Tracking System", "Warehouse Management"],
            "construction": ["Project Management", "Resource Planning", "Time Tracking", "Document Management"],
            "consulting": ["Client Management", "Project Tracking", "Time Billing", "Document Sharing"],
            "small_businesses": ["Website Development", "Online Presence", "Basic IT Setup", "Digital Marketing"],
            "startups": ["Complete IT Infrastructure", "Custom Software", "Cloud Solutions", "Digital Platform"],
            "traditional_businesses": ["Digital Transformation", "Online Presence", "Modernization", "Automation"]
        }
        
        patterns = business_patterns.get(category, ["Business", "Company", "Enterprise"])
        needs = it_needs.get(category, ["Digital Transformation", "Automation", "Software Solutions"])
        
        for i in range(count):
            pattern = patterns[i % len(patterns)]
            business_name = f"{pattern} {location} {i+1}"
            
            # Generate realistic business contact
            phone_number = f"+91 {random.randint(80000, 99999)}{random.randint(10000, 99999)}"
            email = f"info@{business_name.lower().replace(' ', '')}.com"
            
            prospect = {
                'business_name': business_name,
                'address': f"{random.randint(1, 500)} {category.title()} Street, {location}",
                'contact': phone_number,
                'email': email,
                'location': location,
                'category': category,
                'source': 'IT Client Targeting (Demo Data)',
                'it_needs': random.choice(needs),
                'business_type': category,
                'priority': self._assess_it_priority(category),
                'website': f"https://{business_name.lower().replace(' ', '')}.com" if random.random() > 0.4 else "",
                'scraped_at': datetime.now().isoformat(),
                'notes': f"Potential client for {random.choice(needs)} - Contact for {self._get_service_offering(category)}",
                'data_type': 'DEMONSTRATION',
                'note': 'This is demonstration IT client data for testing purposes. Contact details may not be real.'
            }
            
            # Add specific IT requirements based on business type
            prospect['recommended_solutions'] = ", ".join(self._get_recommended_solutions(category))
            prospect['estimated_budget'] = self._estimate_budget_range(category)
            prospect['urgency'] = self._assess_urgency(category)
            prospect['it_priority'] = prospect['priority']  # Copy priority to it_priority for display
            prospect['lead_score'] = str(self._calculate_lead_score(category, prospect))
            
            if self.utils.is_valid_business_data(prospect):
                prospects.append(prospect)
        
        return prospects
    
    def _assess_it_priority(self, category: str) -> str:
        """Assess the IT service priority for different business types."""
        high_priority = ["restaurants", "retail_shops", "medical_clinics", "educational_institutes", "startups"]
        medium_priority = ["real_estate", "manufacturing", "accounting_firms", "law_firms", "small_businesses"]
        
        if category in high_priority:
            return "High"
        elif category in medium_priority:
            return "Medium"
        else:
            return "Low"
    
    def _assess_urgency(self, category: str) -> str:
        """Assess urgency of IT needs."""
        urgent = ["startups", "traditional_businesses", "small_businesses"]
        moderate = ["restaurants", "retail_shops", "medical_clinics"]
        
        if category in urgent:
            return "Urgent - Needs immediate digital presence"
        elif category in moderate:
            return "Moderate - Can improve operations significantly"
        else:
            return "Standard - Gradual implementation possible"
    
    def _get_service_offering(self, category: str) -> str:
        """Get service offering pitch based on business type."""
        offerings = {
            "restaurants": "online ordering and digital menu solutions",
            "retail_shops": "e-commerce platform and inventory management",
            "medical_clinics": "patient management and digital health records",
            "educational_institutes": "learning management and student portals",
            "real_estate": "property management and CRM solutions",
            "manufacturing": "ERP implementation and process automation",
            "accounting_firms": "cloud accounting and client management systems",
            "law_firms": "case management and document automation",
            "beauty_salons": "appointment booking and customer management",
            "fitness_centers": "membership management and class booking systems",
            "automobile_dealers": "dealer management and inventory systems",
            "hotels": "hotel management and booking systems",
            "logistics": "fleet management and tracking solutions",
            "construction": "project management and digital documentation",
            "consulting": "CRM and project management solutions",
            "small_businesses": "complete digital transformation package",
            "startups": "end-to-end IT infrastructure setup",
            "traditional_businesses": "modernization and digital presence solutions"
        }
        
        return offerings.get(category, "custom IT solutions and digital transformation")
    
    def _get_recommended_solutions(self, category: str) -> List[str]:
        """Get recommended IT solutions for specific business types."""
        solutions = {
            "restaurants": ["Cloud POS System", "Online Ordering Platform", "Digital Menu", "Customer Loyalty App"],
            "retail_shops": ["E-commerce Website", "Inventory Management", "Customer CRM", "Payment Gateway"],
            "medical_clinics": ["EMR System", "Patient Portal", "Appointment Scheduling", "Billing Software"],
            "educational_institutes": ["LMS Platform", "Student Information System", "E-learning Portal", "Virtual Classroom"],
            "real_estate": ["Property Management CRM", "Lead Generation System", "Virtual Tour Platform", "Document Management"],
            "manufacturing": ["ERP Implementation", "Production Planning Software", "Quality Management", "IoT Solutions"],
            "accounting_firms": ["Cloud Accounting Software", "Tax Preparation System", "Client Portal", "Document Management"],
            "law_firms": ["Practice Management Software", "Time & Billing System", "Document Repository", "Client Communication Portal"],
            "beauty_salons": ["Appointment Booking App", "Staff Scheduling", "Inventory Management", "Customer Database"],
            "fitness_centers": ["Membership Management", "Class Booking System", "Payment Processing", "Fitness Tracking App"],
            "automobile_dealers": ["Dealer Management System", "Inventory Tracking", "Service Scheduling", "CRM Integration"],
            "hotels": ["Hotel Management System", "Online Booking Engine", "Guest Services App", "Revenue Management"],
            "logistics": ["Fleet Management System", "Route Optimization", "Shipment Tracking", "Warehouse Management"],
            "construction": ["Project Management Platform", "Resource Planning", "Time Tracking", "Safety Management"],
            "consulting": ["CRM System", "Project Management", "Time Tracking", "Knowledge Management"],
            "small_businesses": ["Business Website", "Social Media Setup", "Basic CRM", "Online Payment System"],
            "startups": ["Complete IT Infrastructure", "Custom Software Development", "Cloud Migration", "Digital Platform"],
            "traditional_businesses": ["Digital Transformation Roadmap", "Website Development", "Process Automation", "Online Presence"]
        }
        
        return solutions.get(category, ["Custom Software Development", "IT Consulting", "Digital Transformation"])
    
    def _estimate_budget_range(self, category: str) -> str:
        """Estimate budget range for IT solutions based on business type."""
        budget_ranges = {
            "restaurants": "₹50K - ₹2L",
            "retail_shops": "₹75K - ₹3L", 
            "medical_clinics": "₹1L - ₹5L",
            "educational_institutes": "₹2L - ₹10L",
            "real_estate": "₹1L - ₹4L",
            "manufacturing": "₹3L - ₹15L",
            "accounting_firms": "₹75K - ₹3L",
            "law_firms": "₹1L - ₹4L",
            "beauty_salons": "₹30K - ₹1.5L",
            "fitness_centers": "₹50K - ₹2L",
            "automobile_dealers": "₹1.5L - ₹6L",
            "hotels": "₹2L - ₹8L",
            "logistics": "₹1.5L - ₹7L",
            "construction": "₹2L - ₹10L",
            "consulting": "₹75K - ₹3L",
            "small_businesses": "₹25K - ₹1L",
            "startups": "₹1L - ₹5L",
            "traditional_businesses": "₹50K - ₹2L"
        }
        
        return budget_ranges.get(category, "₹50K - ₹2L")
    
    def _calculate_lead_score(self, category: str, prospect: Dict[str, Any]) -> int:
        """Calculate lead score based on business type and characteristics."""
        base_score = 50
        
        # High-priority business types get higher scores
        high_priority_categories = ["medical_clinics", "educational_institutes", "manufacturing", "hotels"]
        medium_priority_categories = ["restaurants", "retail_shops", "real_estate", "automobile_dealers"]
        
        if category in high_priority_categories:
            base_score += 30
        elif category in medium_priority_categories:
            base_score += 20
        else:
            base_score += 10
            
        # Add randomness for realistic variation
        variation = random.randint(-15, 15)
        final_score = max(10, min(100, base_score + variation))
        
        return final_score
        
        return budget_ranges.get(category, "₹50K - ₹3L")
