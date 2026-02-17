import streamlit as st
import pandas as pd
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Law Study Aid Finder",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .resource-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 4px solid #1f77b4;
    }
    .resource-title {
        font-size: 1.3em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .content-section {
        margin: 8px 0;
        font-size: 0.95em;
    }
    .must-have {
        color: #28a745;
        font-weight: 500;
    }
    .neutral {
        color: #6c757d;
        font-style: italic;
    }
    .question-text {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 8px;
        margin-top: 20px;
    }
    /* Question 3 content descriptions should be bold */
    .content-description {
        font-weight: bold;
        margin-bottom: 4px;
        margin-top: 12px;
    }
    /* All radio button options should be normal weight */
    div[data-testid="stRadio"] label p {
        font-weight: normal;
    }
    /* Checkbox labels should also be normal weight */
    div[data-testid="stCheckbox"] label p {
        font-size: 0.95em;
        font-weight: normal;
    }
    /* Horizontal radio button options (Must Have, Neutral, etc.) */
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        font-weight: normal !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the data
@st.cache_data
def load_data():
    """Load the Excel file with study aid resources"""
    df = pd.read_excel('Beta_Study_Aids_v2.xlsx')
    # Replace NaN with empty strings for easier handling
    df = df.fillna('')
    return df

# Content type mapping
CONTENT_MAPPING = {
    "Visual diagrams, like flowcharts that show how concepts fit together or comparison tables that show a side-by-side breakdown of related concepts": {
        "column": "Charts",
        "display": "Visual diagrams"
    },
    "Checklists to help you organize your analysis": {
        "column": "Checklists ",  # Note: there's a space in the column name
        "display": "Checklists"
    },
    "Interactive lessons that blend explanations with practice questions to test your understanding": {
        "column": "Interactive",
        "display": "Interactive lessons"
    },
    "Detailed, in-depth explanations of concepts": {
        "column": "Detailed analysis",
        "display": "Detailed explanations"
    },
    "Quick overview explanations and big picture summaries": {
        "column": "High-Level summary",
        "display": "Quick summaries"
    },
    "Multiple choice practice questions": {
        "column": "MCQ",
        "display": "Multiple choice practice questions"
    },
    "Short answer practice questions": {
        "column": "SQ",
        "display": "Short answer practice questions"
    },
    "Essay practice questions": {
        "column": "EQ",
        "display": "Essay practice questions"
    },
    "Flashcards to test recall": {
        "column": "Flashcards",
        "display": "Flashcards"
    },
    "Mnemonics to help with memorization": {
        "column": "Mnemonics",
        "display": "Mnemonics"
    },
    "Case briefs": {
        "column": "Case Brief",
        "display": "Case briefs"
    },
    "Course outlines": {
        "column": "Outlines",
        "display": "Course outlines"
    }
}

def filter_by_subject(df: pd.DataFrame, subject: str) -> pd.DataFrame:
    """Filter resources by subject"""
    return df[df[subject].str.lower() == 'x']

def filter_by_format(df: pd.DataFrame, format_choices: List[str]) -> pd.DataFrame:
    """Filter resources by study format (supports multiple selections)"""
    if not format_choices:
        return df
    
    format_mapping = {
        "Digital book/e-book": "Digital Access Available",
        "Video Lectures": "Video",
        "Audio Lectures": "Audio",
        "Physical book": "Physical Item in Library Collection"
    }
    
    # Create a mask that is True for any row that matches ANY of the selected formats
    mask = pd.Series([False] * len(df), index=df.index)
    
    for format_choice in format_choices:
        column = format_mapping[format_choice]
        mask = mask | (df[column].str.lower() == 'x')
    
    return df[mask]

def calculate_score(row: pd.Series, preferences: Dict[str, str]) -> Dict:
    """Calculate score based on content preferences"""
    score = 0
    strongly_preferred_matches = []
    somewhat_preferred_matches = []
    
    for question, info in CONTENT_MAPPING.items():
        column = info["column"]
        display = info["display"]
        preference = preferences.get(question, "No Preference")
        
        # Check if resource has this content type
        if row[column] and str(row[column]).lower() == 'x':
            if preference == "Strongly Preferred":
                score += 1
                strongly_preferred_matches.append(display)
            elif preference == "Somewhat Preferred":
                score += 0.5
                somewhat_preferred_matches.append(display)
    
    return {
        "score": score,
        "strongly_preferred": strongly_preferred_matches,
        "somewhat_preferred": somewhat_preferred_matches
    }

def generate_pdf_html(results: List[Dict], subject: str, formats: List[str]) -> str:
    """Generate HTML content for PDF export"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }}
            h1 {{
                color: #1f77b4;
                border-bottom: 3px solid #1f77b4;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #333;
                margin-top: 30px;
            }}
            .print-instructions {{
                background-color: #e7f3ff;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 4px solid #1f77b4;
            }}
            .print-instructions a {{
                color: #1f77b4;
                text-decoration: none;
                font-weight: bold;
                cursor: pointer;
            }}
            .print-instructions a:hover {{
                text-decoration: underline;
            }}
            .criteria {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .resource {{
                border-left: 4px solid #1f77b4;
                padding: 15px;
                margin-bottom: 20px;
                background-color: #f8f9fa;
                page-break-inside: avoid;
            }}
            .resource-title {{
                font-size: 1.2em;
                font-weight: bold;
                color: #1f77b4;
                margin-bottom: 10px;
            }}
            .strongly-preferred {{
                color: #28a745;
                font-weight: 500;
            }}
            .somewhat-preferred {{
                color: #6c757d;
                font-style: italic;
            }}
            .links {{
                margin-top: 10px;
            }}
            .links a {{
                color: #1f77b4;
                text-decoration: none;
                margin-right: 15px;
            }}
            @media print {{
                body {{ margin: 20px; }}
                .print-instructions {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <h1>📚 Your Recommended Study Aids</h1>
        
        <div class="print-instructions">
            💡 <strong>To save as PDF:</strong> <a href="javascript:window.print()">Click here to open the print dialog</a>, then choose "Save as PDF" as your printer.
        </div>
        
        <div class="criteria">
            <strong>Your Selections:</strong><br>
            <strong>Subject:</strong> {subject}<br>
            <strong>Study Formats:</strong> {', '.join(formats)}<br>
            <strong>Results Found:</strong> {len(results)}
        </div>
        
        <h2>Recommended Resources</h2>
        <p>Resources are displayed according to how well they match your preferences.</p>
    """
    
    for idx, result in enumerate(results, 1):
        resource = result['resource']
        score_info = result['score_info']
        
        title = resource['Title to Display']
        publisher = resource['Publisher']
        
        html += f"""
        <div class="resource">
            <div class="resource-title">{idx}. {title} ({publisher})</div>
        """
        
        if score_info['strongly_preferred']:
            sp_text = ", ".join(score_info['strongly_preferred'])
            html += f'<div class="strongly-preferred">✓ Strongly Preferred: {sp_text}</div>'
        
        if score_info['somewhat_preferred']:
            swp_text = ", ".join(score_info['somewhat_preferred'])
            html += f'<div class="somewhat-preferred">○ Somewhat Preferred: {swp_text}</div>'
        
        html += '<div class="links">'
        
        catalog_url = resource['Catalog URL']
        if catalog_url and catalog_url.strip():
            html += f'<a href="{catalog_url}">View in Law Library Catalog</a>'
        
        digital_url = resource['Digital Resource URL']
        if digital_url and digital_url.strip():
            html += f'<a href="{digital_url}">View Digital Resource</a>'
        
        html += '</div></div>'
    
    html += """
    </body>
    </html>
    """
    return html

def display_results(results: List[Dict], subject: str = None, formats: List[str] = None):
    """Display the sorted and formatted results"""
    if not results:
        st.warning("No resources match your criteria. Try adjusting your preferences.")
        return
    
    st.markdown("---")
    st.header(f"📚 Your Recommended Study Aids ({len(results)} resources found)")
    st.markdown("Resources are displayed according to how well the resource matches your preferences.")
    
    # Add button to open results in new page (moved under description)
    if subject and formats:
        import json
        pdf_html = generate_pdf_html(results, subject, formats)
        # Escape the HTML for JavaScript
        escaped_html = json.dumps(pdf_html)
        
        st.markdown(
            f"""
            <script>
            function openResultsPage() {{
                var newWindow = window.open('', '_blank');
                newWindow.document.write({escaped_html});
                newWindow.document.close();
            }}
            </script>
            <button onclick="openResultsPage()" style="display: inline-block; padding: 0.5rem 1rem; 
            background-color: #1f77b4; color: white; border: none; border-radius: 0.3rem; 
            font-weight: 500; margin-top: 0.5rem; margin-bottom: 1rem; cursor: pointer; 
            font-size: 1rem;">📄 Open Results in New Page</button>
            """,
            unsafe_allow_html=True
        )
    
    for idx, result in enumerate(results, 1):
        resource = result['resource']
        score_info = result['score_info']
        
        # Create the resource card
        with st.container():
            # Title and Publisher
            title = resource['Title to Display']
            publisher = resource['Publisher']
            st.markdown(f'<div class="resource-title">{title} ({publisher})</div>', 
                       unsafe_allow_html=True)
            
            # Strongly Preferred content types
            if score_info['strongly_preferred']:
                sp_text = ", ".join(score_info['strongly_preferred'])
                st.markdown(f'<div class="content-section must-have">✓ Strongly Preferred: {sp_text}</div>', 
                           unsafe_allow_html=True)
            
            # Somewhat Preferred content types
            if score_info['somewhat_preferred']:
                swp_text = ", ".join(score_info['somewhat_preferred'])
                st.markdown(f'<div class="content-section neutral">○ Somewhat Preferred: {swp_text}</div>', 
                           unsafe_allow_html=True)
            
            # Links
            col1, col2 = st.columns(2)
            
            with col1:
                catalog_url = resource['Catalog URL']
                if catalog_url and catalog_url.strip():
                    st.markdown(f'[📖 View in Law Library Catalog]({catalog_url})')
                elif resource['Digital Resource URL'] and resource['Digital Resource URL'].strip():
                    # Show digital URL if no catalog URL
                    st.markdown(f'[🔗 View the Digital Resource]({resource["Digital Resource URL"]})')
            
            with col2:
                digital_url = resource['Digital Resource URL']
                if digital_url and digital_url.strip() and catalog_url and catalog_url.strip():
                    st.markdown(f'[🔗 View the Digital Resource]({digital_url})')
            
            st.markdown("---")


def main():
    # Title and description
    st.title("📚 Law Study Aid Finder")
    st.markdown("Answer a few questions to find the perfect study aids for your needs.")
    
    # Load data
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Create the questionnaire
    with st.form("study_aid_questionnaire"):
        st.markdown('<p class="question-text">1. What subject are you studying? (Select one)</p>', unsafe_allow_html=True)
        subject = st.radio(
            "Select subject:",
            ["Civil Procedure", "Contracts"],
            index=None,
            label_visibility="collapsed"
        )
        
        st.markdown('<p class="question-text">2. How do you prefer to study? (Select all that apply)</p>', unsafe_allow_html=True)
        
        # Use checkboxes for multi-select in a single column
        study_formats = []
        
        if st.checkbox("Digital book/e-book", key="format_digital"):
            study_formats.append("Digital book/e-book")
        if st.checkbox("Physical book", key="format_physical"):
            study_formats.append("Physical book")
        if st.checkbox("Audio lectures", key="format_audio"):
            study_formats.append("Audio Lectures")
        if st.checkbox("Video lectures", key="format_video"):
            study_formats.append("Video Lectures")
        
        st.markdown('<p class="question-text">3. What specific content do you want to see in your study aid?</p>', unsafe_allow_html=True)
        st.markdown("Select your preference for each type of content:")
        
        preferences = {}
        
        # Show full text for each content type option with bold descriptions
        for i, (question, info) in enumerate(CONTENT_MAPPING.items()):
            # Display the description in bold as a separate element
            st.markdown(f'<p class="content-description">{question}</p>', unsafe_allow_html=True)
            # Radio button with hidden label
            preferences[question] = st.radio(
                question,  # Keep for accessibility, but will style to hide
                ["Strongly Preferred", "Somewhat Preferred", "No Preference"],
                index=1,  # Default to Somewhat Preferred (middle option)
                key=f"pref_{i}",
                horizontal=True,
                label_visibility="collapsed"  # Hide the label since we show it above
            )
        
        # Submit button
        submitted = st.form_submit_button("🔍 Find My Study Aids", use_container_width=True)
    
    # Process the form submission
    if submitted:
        # Validate inputs
        if not subject:
            st.error("Please select a subject.")
            return
        if not study_formats:
            st.error("Please select at least one study format.")
            return
        
        # Filter by subject
        filtered_df = filter_by_subject(df, subject)
        
        # Filter by format (now handles multiple selections)
        filtered_df = filter_by_format(filtered_df, study_formats)
        
        # Calculate scores for each resource
        results = []
        for idx, row in filtered_df.iterrows():
            score_info = calculate_score(row, preferences)
            
            # Only include resources with score > 0
            if score_info['score'] > 0:
                results.append({
                    'resource': row,
                    'score_info': score_info,
                    'title': row['Title to Display']
                })
        
        # Sort by score (descending) then by title (alphabetically)
        results.sort(key=lambda x: (-x['score_info']['score'], x['title'].lower()))
        
        # Display results
        display_results(results, subject, study_formats)

if __name__ == "__main__":
    main()
