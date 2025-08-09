import streamlit as st
import pandas as pd
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/scraping.log'),
        logging.StreamHandler()
    ]
)

# Import our modules
from database import DatabaseManager
from utils import ScrapingUtils
from scraper import BusinessScraper

# Page configuration
st.set_page_config(
    page_title="Client Hunter - Business Scraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .scraping-status {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-status {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-status {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .warning-status {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()

if 'utils' not in st.session_state:
    st.session_state.utils = ScrapingUtils()

if 'scraper' not in st.session_state:
    st.session_state.scraper = BusinessScraper(
        st.session_state.utils,
        st.session_state.db_manager
    )

if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = None

if 'current_businesses' not in st.session_state:
    st.session_state.current_businesses = []

def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Client Hunter")
        st.markdown("**Intelligent Business Directory Scraper**")
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar
    setup_sidebar()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["Scraper", "Dashboard", "Map View", "Analytics"])
    
    with tab1:
        scraper_interface()
    
    with tab2:
        dashboard_interface()
    
    with tab3:
        map_interface()
    
    with tab4:
        analytics_interface()

def setup_sidebar():
    """Setup sidebar with navigation and controls."""
    with st.sidebar:
        st.markdown("## Control Panel")
        
        # Quick stats
        stats = st.session_state.db_manager.get_statistics()
        st.metric("Total Businesses", stats['total_businesses'])
        
        # Recent activity
        if stats['recent_activity']:
            st.markdown("### Recent Activity")
            for activity in stats['recent_activity'][:3]:
                st.write(f"**{activity['date']}**: {activity['count']} businesses")
        
        st.markdown("---")
        
        # Export functionality
        st.markdown("### Export Data")
        
        if st.button("Export CSV", key="export_csv_btn"):
            export_data()
        
        if st.button("Clear Data", key="clear_data_btn"):
            if st.session_state.get('confirm_clear', False):
                clear_database()
            else:
                st.session_state.confirm_clear = True
                st.warning("Click again to confirm clearing all data!")
                st.rerun()
        
        st.markdown("---")
        
        # Settings
        st.markdown("### Settings")
        
        # Scraping sources
        st.markdown("**Scraping Sources**")
        
        # Initialize default sources if not set
        if 'selected_sources' not in st.session_state:
            st.session_state.selected_sources = ['justdial', 'indiamart', 'it_clients']
        
        sources = {
            'JustDial': st.checkbox('JustDial', value='justdial' in st.session_state.selected_sources, key="source_justdial"),
            'IndiaMART': st.checkbox('IndiaMART', value='indiamart' in st.session_state.selected_sources, key="source_indiamart"),
            'Yellow Pages': st.checkbox('Yellow Pages', value='yellowpages' in st.session_state.selected_sources, key="source_yellowpages"),
            'Google Maps': st.checkbox('Google Maps', value='googlemaps' in st.session_state.selected_sources, key="source_googlemaps"),
            'IT Clients': st.checkbox('IT Service Prospects', value='it_clients' in st.session_state.selected_sources, key="source_it_clients",
                                    help="Target businesses needing IT services and digital transformation")
        }
        
        # Update selected sources based on checkboxes
        st.session_state.selected_sources = []
        for source, selected in sources.items():
            if selected:
                if source == 'IT Clients':
                    st.session_state.selected_sources.append('it_clients')
                elif source == 'Yellow Pages':
                    st.session_state.selected_sources.append('yellowpages')
                elif source == 'Google Maps':
                    st.session_state.selected_sources.append('googlemaps')
                else:
                    st.session_state.selected_sources.append(source.lower())
        
        # Show currently selected sources
        if st.session_state.selected_sources:
            st.success(f"Active Sources: {', '.join(st.session_state.selected_sources)}")
        else:
            st.warning("No sources selected! Please select at least one source.")
        
        
        # Max results per source
        st.session_state.max_results = st.slider(
            "Max Results per Source", 
            min_value=10, 
            max_value=200, 
            value=50, 
            step=10
        )

def scraper_interface():
    """Interface for scraping operations."""
    st.markdown("## Start Scraping")
    
    # Input form
    with st.form("scraping_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            location = st.text_input(
                "Enter Location",
                placeholder="e.g., Mumbai, 400001, Connaught Place Delhi",
                help="Enter city name, pincode, or specific address"
            )
        
        with col2:
            category_options = [
                "General Business Search",
                "IT Service Prospects",
                "Small Businesses Needing Websites", 
                "Healthcare Providers (Digital Systems)",
                "Educational Institutes (Tech Upgrade)",
                "Retail Businesses (E-commerce Setup)",
                "Professional Services (CRM/Software)",
                "Manufacturing Units (Digital Transformation)",
                "Startups (Complete IT Solutions)"
            ]
            
            category_type = st.selectbox(
                "Target Category",
                category_options,
                help="Choose specific business types for targeted prospecting"
            )
            
            if category_type == "General Business Search":
                category = st.text_input(
                    "Custom Category",
                    placeholder="e.g., restaurants, shops",
                    help="Enter custom business category"
                )
            else:
                category = category_type
        
        # Scraping options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scrape_type = st.selectbox(
                "Scraping Mode",
                ["Quick Scrape", "Comprehensive Scrape", "Custom"],
                help="Quick: Fast sources only, Comprehensive: All sources"
            )
        
        with col2:
            if scrape_type == "Custom":
                max_results = st.number_input(
                    "Max Results per Source",
                    min_value=10,
                    max_value=500,
                    value=st.session_state.max_results
                )
            else:
                max_results = 50 if scrape_type == "Quick Scrape" else 100
        
        with col3:
            headless_mode = st.checkbox(
                "Headless Browser",
                value=True,
                help="Run browser in background (recommended)"
            )
        
        # Submit button
        submitted = st.form_submit_button(
            "Start Scraping",
            type="primary",
            use_container_width=True
        )
    
    # Handle form submission
    if submitted and location:
        if not st.session_state.selected_sources:
            st.error("Please select at least one scraping source!")
            return
        
        # Start scraping
        with st.spinner("Scraping in progress... This may take a few minutes."):
            try:
                # Run scraping with selected sources
                if scrape_type == "Quick Scrape":
                    results = asyncio.run(
                        st.session_state.scraper.quick_scrape(
                            location, 
                            category, 
                            selected_sources=st.session_state.selected_sources
                        )
                    )
                elif scrape_type == "Comprehensive Scrape":
                    results = asyncio.run(
                        st.session_state.scraper.comprehensive_scrape(
                            location, 
                            category, 
                            selected_sources=st.session_state.selected_sources
                        )
                    )
                else:  # Custom
                    results = asyncio.run(
                        st.session_state.scraper.scrape_location(
                            location, 
                            category, 
                            sources=st.session_state.selected_sources,
                            max_results_per_source=max_results
                        )
                    )
                
                st.session_state.scraping_results = results
                
                # Display results
                display_scraping_results(results, context="new_results")
                
            except Exception as e:
                st.error(f" Scraping failed: {str(e)}")
                logging.error(f"Scraping error: {e}")
    
    elif submitted and not location:
        st.error("Please enter a location to scrape!")
    
    # Display previous results if available
    if st.session_state.scraping_results:
        st.markdown("---")
        st.markdown("## Last Scraping Results")
        display_scraping_results(st.session_state.scraping_results, context="previous_results")

def display_scraping_results(results: Dict[str, Any], context: str = "default"):
    """Display scraping results in a formatted way."""
    
    # Success message
    if results['total_businesses'] > 0:
        st.markdown(
            f'<div class="scraping-status success-status">'
            f'<strong>Scraping Completed Successfully!</strong><br>'
            f'Found {results["total_businesses"]} businesses from {len(results["sources_scraped"])} sources'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="scraping-status warning-status">'
            f'<strong>No businesses found</strong> for the given location and criteria.'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Results breakdown
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Location", results['location'])
    
    with col2:
        st.metric("Category", results['category'] or "All")
    
    with col3:
        st.metric("Total Found", results['total_businesses'])
    
    with col4:
        st.metric("Sources Used", len(results['sources_scraped']))
    
    # Source breakdown
    if results['businesses_by_source']:
        st.markdown("### Results by Source")
        source_df = pd.DataFrame([
            {'Source': source.title(), 'Count': count}
            for source, count in results['businesses_by_source'].items()
        ])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(source_df, use_container_width=True)
        
        with col2:
            if not source_df.empty:
                fig = px.bar(
                    source_df, 
                    x='Source', 
                    y='Count',
                    title="Businesses Found by Source",
                    color='Count',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig, use_container_width=True, key=f"source_chart_{context}")
    
    # Errors (if any)
    if results['errors']:
        st.markdown("### Errors Encountered")
        for error in results['errors']:
            st.warning(error)

def dashboard_interface():
    """Main dashboard interface."""
    st.markdown("## Business Dashboard")
    
    # Filters
    with st.expander("Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            location_filter = st.text_input("Location Filter")

        with col2:
            category_filter = st.text_input("Category Filter")
        
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=[datetime.now() - timedelta(days=30), datetime.now()],
                max_value=datetime.now()
            )
        
        with col4:
            search_term = st.text_input("🔍 Search Businesses")
    
    # Get filtered data
    if search_term:
        businesses = st.session_state.db_manager.search_businesses(search_term)
    else:
        start_date = date_range[0].strftime('%Y-%m-%d') if len(date_range) > 0 else None
        end_date = date_range[1].strftime('%Y-%m-%d') if len(date_range) > 1 else None
        
        businesses = st.session_state.db_manager.get_businesses(
            location=location_filter or None,
            category=category_filter or None,
            start_date=start_date,
            end_date=end_date
        )
    
    st.session_state.current_businesses = businesses
    
    if businesses:
        # Convert to DataFrame
        df = pd.DataFrame(businesses)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(" Total Businesses", len(df))
        
        with col2:
            unique_locations = df['location'].nunique()
            st.metric(" Unique Locations", unique_locations)
        
        with col3:
            with_contact = df['contact'].notna().sum()
            st.metric(" With Contact Info", with_contact)
        
        with col4:
            with_website = df['website'].notna().sum()
            st.metric("With Websites", with_website)
        
        # Check if we have IT prospect data
        has_it_data = any(col in df.columns for col in ['lead_score', 'pain_points', 'it_requirements'])
        
        if has_it_data:
            st.markdown("### IT Prospect Insights")
            
            # IT-specific metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'lead_score' in df.columns:
                    high_priority = (df['lead_score'] >= 8).sum()
                    st.metric(" High Priority Leads", high_priority)
            
            with col2:
                if 'it_requirements' in df.columns:
                    website_needs = df['it_requirements'].str.contains('website', case=False, na=False).sum()
                    st.metric("Need Websites", website_needs)
            
            with col3:
                if 'it_requirements' in df.columns:
                    ecommerce_needs = df['it_requirements'].str.contains('e-commerce|online store', case=False, na=False).sum()
                    st.metric("Need E-commerce", ecommerce_needs)
            
            with col4:
                if 'it_requirements' in df.columns:
                    software_needs = df['it_requirements'].str.contains('software|system|CRM|ERP', case=False, na=False).sum()
                    st.metric("Need Software", software_needs)
            
            # Lead score distribution
            if 'lead_score' in df.columns:
                st.markdown("#### Lead Score Distribution")
                score_counts = df['lead_score'].value_counts().sort_index()
                fig_scores = px.bar(
                    x=score_counts.index, 
                    y=score_counts.values,
                    labels={'x': 'Lead Score', 'y': 'Number of Prospects'},
                    title="Lead Score Distribution"
                )
                st.plotly_chart(fig_scores, use_container_width=True, key=f"score_chart_{hash(str(score_counts))}")
        
        # Data table
        st.markdown("### Business Listings")
        
        # Column selection
        display_columns = st.multiselect(
            "Select columns to display:",
            df.columns.tolist(),
            default=['business_name', 'address', 'contact', 'website', 'category', 'location']
        )
        
        if display_columns:
            st.dataframe(
                df[display_columns],
                use_container_width=True,
                height=400
            )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"businesses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    else:
        st.info("No businesses found. Try adjusting your filters or scrape some data first!")

def map_interface():
    """Map visualization interface."""
    st.markdown("## Business Locations")
    
    businesses = st.session_state.current_businesses
    
    if businesses:
        # Filter businesses with coordinates
        map_data = [
            b for b in businesses 
            if b.get('latitude') and b.get('longitude')
        ]
        
        if map_data:
            # Create map
            df_map = pd.DataFrame(map_data)
            
            # Map display
            st.map(
                df_map[['latitude', 'longitude']],
                zoom=10
            )
            
            # Additional map info
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Businesses on Map", len(map_data))
            
            with col2:
                coverage = (len(map_data) / len(businesses)) * 100
                st.metric("Location Coverage", f"{coverage:.1f}%")
            
            # Detailed map view with folium (if available)
            try:
                import folium
                from streamlit_folium import folium_static
                
                if st.checkbox("Show Detailed Map"):
                    create_folium_map(map_data)
            
            except ImportError:
                st.info("Install folium and streamlit-folium for enhanced map features")

        else:
            st.warning("No businesses with location data found. Geocoding may be needed.")
    
    else:
        st.info("No business data available for mapping.")

def create_folium_map(map_data: List[Dict]):
    """Create a detailed Folium map."""
    try:
        import folium
        from streamlit_folium import folium_static
        
        # Calculate center
        center_lat = sum(b['latitude'] for b in map_data) / len(map_data)
        center_lon = sum(b['longitude'] for b in map_data) / len(map_data)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Add markers
        for business in map_data:
            popup_text = f"""
            <b>{business.get('business_name', 'Unknown')}</b><br>
            {business.get('address', 'No address')}<br>
            {business.get('contact', 'No contact')}<br>
            {business.get('category', 'No category')}
            """
            
            folium.Marker(
                [business['latitude'], business['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=business.get('business_name', 'Business'),
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Display map
        folium_static(m, width=700, height=500)
    
    except Exception as e:
        st.error(f"Error creating detailed map: {e}")

def analytics_interface():
    """Analytics and insights interface."""
    st.markdown("## Analytics & Insights")
    
    businesses = st.session_state.current_businesses
    
    if businesses:
        df = pd.DataFrame(businesses)
        
        # Time series analysis
        if 'scraped_at' in df.columns:
            df['scraped_date'] = pd.to_datetime(df['scraped_at']).dt.date
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Scraping Activity Over Time")
                daily_counts = df.groupby('scraped_date').size().reset_index(name='count')
                
                fig = px.line(
                    daily_counts,
                    x='scraped_date',
                    y='count',
                    title="Businesses Scraped Daily"
                )
                st.plotly_chart(fig, use_container_width=True, key="daily_activity_chart")
            
            with col2:
                st.markdown("### 🏷️ Category Distribution")
                category_counts = df['category'].value_counts().head(10)
                
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Top 10 Categories"
                )
                st.plotly_chart(fig, use_container_width=True, key="category_pie_chart")
        
        # Location analysis
        st.markdown("### 📍 Location Analysis")
        location_stats = df.groupby('location').agg({
            'business_name': 'count',
            'contact': lambda x: x.notna().sum(),
            'website': lambda x: x.notna().sum()
        }).reset_index()
        
        location_stats.columns = ['Location', 'Total Businesses', 'With Contact', 'With Website']
        location_stats['Contact %'] = (location_stats['With Contact'] / location_stats['Total Businesses'] * 100).round(1)
        location_stats['Website %'] = (location_stats['With Website'] / location_stats['Total Businesses'] * 100).round(1)
        
        st.dataframe(location_stats, use_container_width=True)
        
        # Source analysis
        if 'source' in df.columns:
            st.markdown("### 🔍 Source Performance")
            source_stats = df.groupby('source').agg({
                'business_name': 'count',
                'contact': lambda x: x.notna().sum(),
                'website': lambda x: x.notna().sum()
            }).reset_index()
            
            source_stats.columns = ['Source', 'Total', 'With Contact', 'With Website']
            
            fig = px.bar(
                source_stats,
                x='Source',
                y='Total',
                title="Businesses by Source",
                color='Total'
            )
            st.plotly_chart(fig, use_container_width=True, key="source_performance_chart")
    
    else:
        st.info("No data available for analytics.")

def export_data():
    """Export current data to CSV."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"businesses_export_{timestamp}.csv"
        
        # Get all businesses from database
        businesses = st.session_state.db_manager.get_businesses()
        
        if not businesses:
            st.error(" No data to export")
            return
        
        # Create CSV content in memory
        import csv
        import io
        
        output = io.StringIO()
        fieldnames = ['business_name', 'contact', 'address', 'website', 
                     'category', 'location', 'scraped_at', 'source']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for business in businesses:
            row = {field: business.get(field, '') for field in fieldnames}
            writer.writerow(row)
        
        csv_data = output.getvalue()
        output.close()
        
        # Provide download button
        st.download_button(
            label="Download CSV File",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            key="download_csv"
        )
        
        st.success(f" {len(businesses)} businesses ready for download!")
    
    except Exception as e:
        st.error(f"❌ Export error: {e}")

def clear_database():
    """Clear all data from database."""
    try:
        # Check if there's any data to clear
        businesses = st.session_state.db_manager.get_businesses()
        if not businesses:
            st.info(" Database is already empty!")
            return
        
        # Clear all data from database
        with sqlite3.connect(st.session_state.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM businesses")
            cursor.execute("DELETE FROM scraping_sessions")
            conn.commit()
        
        # Clear session state
        if 'current_businesses' in st.session_state:
            st.session_state.current_businesses = []
        if 'scraping_results' in st.session_state:
            st.session_state.scraping_results = None
        if 'confirm_clear' in st.session_state:
            del st.session_state.confirm_clear
        
        st.success(f" Database cleared successfully! Removed {len(businesses)} businesses.")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    main()
