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
    .score-badge {
        background-color: #1f77b4;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.9em;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .question-text {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 8px;
        margin-top: 20px;
    }
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stRadio"] label p {
        font-size: 0.95em;
        font-weight: normal;
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
    must_have_matches = []
    neutral_matches = []
    
    for question, info in CONTENT_MAPPING.items():
        column = info["column"]
        display = info["display"]
        preference = preferences.get(question, "Do Not Want")
        
        # Check if resource has this content type
        if row[column] and str(row[column]).lower() == 'x':
            if preference == "Must Have":
                score += 1
                must_have_matches.append(display)
            elif preference == "Neutral":
                score += 0.5
                neutral_matches.append(display)
    
    return {
        "score": score,
        "must_have": must_have_matches,
        "neutral": neutral_matches
    }

def display_results(results: List[Dict]):
    """Display the sorted and formatted results"""
    if not results:
        st.warning("No resources match your criteria. Try adjusting your preferences.")
        return
    
    st.markdown("---")
    st.header(f"📚 Your Recommended Study Aids ({len(results)} resources found)")
    st.markdown("Resources are sorted by match score (highest first), then alphabetically.")
    
    for idx, result in enumerate(results, 1):
        resource = result['resource']
        score_info = result['score_info']
        
        # Create the resource card
        with st.container():
            # Score badge
            st.markdown(f'<div class="score-badge">Match Score: {score_info["score"]}</div>', 
                       unsafe_allow_html=True)
            
            # Title and Publisher
            title = resource['Title to Display']
            publisher = resource['Publisher']
            st.markdown(f'<div class="resource-title">{title} ({publisher})</div>', 
                       unsafe_allow_html=True)
            
            # Must Have content types
            if score_info['must_have']:
                must_have_text = ", ".join(score_info['must_have'])
                st.markdown(f'<div class="content-section must-have">✓ Must Have: {must_have_text}</div>', 
                           unsafe_allow_html=True)
            
            # Neutral content types
            if score_info['neutral']:
                neutral_text = ", ".join(score_info['neutral'])
                st.markdown(f'<div class="content-section neutral">○ Also includes: {neutral_text}</div>', 
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
        
        # Use checkboxes for multi-select
        study_formats = []
        col1, col2 = st.columns(2)
        
        with col1:
            if st.checkbox("Digital book/e-book", key="format_digital"):
                study_formats.append("Digital book/e-book")
            if st.checkbox("Video Lectures", key="format_video"):
                study_formats.append("Video Lectures")
        
        with col2:
            if st.checkbox("Audio Lectures", key="format_audio"):
                study_formats.append("Audio Lectures")
            if st.checkbox("Physical book", key="format_physical"):
                study_formats.append("Physical book")
        
        st.markdown('<p class="question-text">3. What specific content do you want to see in your study aid?</p>', unsafe_allow_html=True)
        st.markdown("Select 'Must Have,' 'Neutral,' or 'Do Not Want' for each:")
        
        preferences = {}
        
        # Show full text for each content type option
        for i, (question, info) in enumerate(CONTENT_MAPPING.items()):
            # Display full question text without truncation
            preferences[question] = st.radio(
                question,  # Show complete text
                ["Must Have", "Neutral", "Do Not Want"],
                index=1,  # Default to Neutral
                key=f"pref_{i}",
                horizontal=True
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
        display_results(results)

if __name__ == "__main__":
    main()
