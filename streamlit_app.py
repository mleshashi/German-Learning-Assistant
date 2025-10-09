"""
German Learning Assistant - Streamlit Dashboard
Beautiful UI for personalized German learning with daily lessons
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import GermanLearningOrchestrator
from agents.progress_tracker import ProgressTracker

# Page configuration
st.set_page_config(
    page_title="German Learning Assistant",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .lesson-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = "default_user"
if 'progress_tracker' not in st.session_state:
    st.session_state.progress_tracker = ProgressTracker(st.session_state.user_id)
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = GermanLearningOrchestrator()
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Helper function to run async code
def run_async(coro):
    """Run async function in streamlit"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Main title
st.markdown('<h1 class="main-header">🇩🇪 German Learning Assistant</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Navigation")
    
    page = st.radio(
        "Choose a section:",
        ["📊 Dashboard", "📚 Daily Lesson", "💬 Conversation", 
         "📖 Vocabulary", "📝 Grammar", "📈 Progress"]
    )
    
    st.markdown("---")
    
    # Quick stats
    progress = st.session_state.progress_tracker.load_progress()
    st.metric("🔥 Streak", f"{progress['learning_streak']} days")
    st.metric("📊 Level", progress['current_level'])
    st.metric("📚 Words", len(progress['vocabulary_learned']))

# Dashboard Page
if page == "📊 Dashboard":
    st.header("Welcome to Your German Learning Dashboard!")
    
    progress = st.session_state.progress_tracker.load_progress()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{progress['learning_streak']}</div>
            <div class="stat-label">🔥 Day Streak</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{progress['current_level']}</div>
            <div class="stat-label">📊 Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(progress['vocabulary_learned'])}</div>
            <div class="stat-label">📚 Words</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{progress['total_sessions']}</div>
            <div class="stat-label">✅ Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("📚 Start Today's Lesson", use_container_width=True, key="dash_lesson")
    with col2:
        st.button("💬 Practice Conversation", use_container_width=True, key="dash_conv")
    with col3:
        st.button("📊 View Progress", use_container_width=True, key="dash_progress")

# Daily Lesson Page
elif page == "📚 Daily Lesson":
    st.header("📚 Your Personalized Daily Lesson")
    
    with st.spinner("Generating your lesson..."):
        daily_lesson = run_async(st.session_state.progress_tracker.generate_daily_lesson())
    
    # Lesson info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="lesson-card">
            <h3>🎯 Lesson #{daily_lesson['lesson_number']}</h3>
            <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
            <p><strong>Level:</strong> {daily_lesson['user_level']} → {daily_lesson['target_level']}</p>
            <p><strong>Duration:</strong> {daily_lesson['estimated_duration']}</p>
            <p><strong>Focus:</strong> {', '.join(daily_lesson['focus_areas'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.info(daily_lesson['motivation_message'])
    
    st.markdown("---")
    
    # Warm-up
    st.subheader("🔥 Warm-up: Vocabulary Review")
    lesson_content = daily_lesson['lesson_content']
    
    if lesson_content['warm_up']['content']:
        st.write(lesson_content['warm_up']['instruction'])
        cols = st.columns(min(5, len(lesson_content['warm_up']['content'])))
        for idx, word in enumerate(lesson_content['warm_up']['content']):
            with cols[idx % 5]:
                st.info(f"**{word}**")
    else:
        st.info("Complete some lessons to build your vocabulary!")
    
    st.markdown("---")
    
    # Main exercises
    st.subheader("🎯 Main Exercises")
    
    for idx, exercise in enumerate(lesson_content['main_exercises'], 1):
        st.markdown(f"### Exercise {idx}: {exercise['type'].replace('_', ' ').title()}")
        st.write(f"**Focus:** {exercise['focus']}")
        
        if exercise['type'] == 'grammar_analysis':
            user_input = st.text_area(
                "Analyze this sentence:",
                value=exercise['sentence'],
                key=f"grammar_{idx}"
            )
            
            if st.button("Analyze Grammar", key=f"analyze_grammar_{idx}"):
                with st.spinner("Analyzing..."):
                    result = run_async(
                        st.session_state.orchestrator.orchestrate_learning(
                            text=user_input,
                            level=daily_lesson['user_level'],
                            goal="grammar analysis"
                        )
                    )
                    
                    if result['success']:
                        lesson = result['comprehensive_lesson']
                        st.success("✅ Analysis complete!")
                        
                        with st.expander("📚 Grammar Insights"):
                            st.write(f"**Main Structures:** {lesson['grammar_insights'].get('main_structures', 'N/A')}")
                            st.write(f"**Tip:** {lesson['grammar_insights'].get('learning_tip', 'N/A')}")
                        
                        run_async(st.session_state.progress_tracker.track_lesson_completion(result))
        
        elif exercise['type'] == 'vocabulary_building':
            user_word = st.text_input(
                "Analyze this word:",
                value=exercise['word'],
                key=f"vocab_{idx}"
            )
            
            if st.button("Analyze Word", key=f"analyze_vocab_{idx}"):
                with st.spinner("Analyzing..."):
                    result = run_async(
                        st.session_state.orchestrator.orchestrate_learning(
                            text=user_word,
                            level=daily_lesson['user_level'],
                            goal="vocabulary analysis"
                        )
                    )
                    
                    if result['success']:
                        lesson = result['comprehensive_lesson']
                        st.success("✅ Analysis complete!")
                        
                        with st.expander("📖 Vocabulary Insights"):
                            for word, analysis in lesson['vocabulary_insights'].items():
                                st.write(f"**{word}:** {analysis['level']} level")
                                st.write(f"Compound: {'Yes' if analysis['is_compound'] else 'No'}")
                        
                        run_async(st.session_state.progress_tracker.track_lesson_completion(result))

# Conversation Page
elif page == "💬 Conversation":
    st.header("💬 Practice German Conversation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        progress = st.session_state.progress_tracker.load_progress()
        level = st.selectbox("Level:", ["A1", "A2", "B1", "B2", "C1", "C2"], 
                             index=["A1", "A2", "B1", "B2", "C1", "C2"].index(progress['current_level']))
    
    with col2:
        scenario = st.selectbox("Scenario:", 
                                ["casual", "restaurant", "shopping", "travel", "work"])
    
    # Conversation display
    st.subheader("Conversation")
    
    for msg in st.session_state.conversation_history:
        if msg['role'] == 'user':
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 AI:** {msg['content']}")
            if msg.get('translation'):
                st.caption(f"📝 {msg['translation']}")
    
    # User input
    user_message = st.text_input("Your message in German:", key="conv_input")
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        send = st.button("Send", use_container_width=True)
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()
    
    if send and user_message:
        st.session_state.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        with st.spinner("Thinking..."):
            result = run_async(
                st.session_state.orchestrator.orchestrate_learning(
                    text=user_message,
                    level=level,
                    goal="conversation practice",
                    context={"topic": scenario, "scenario": scenario}
                )
            )
            
            if result['success']:
                conv_data = result['comprehensive_lesson'].get('conversation_practice', {})
                
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': conv_data.get('suggested_response', 'Entschuldigung...'),
                    'translation': conv_data.get('translation', '')
                })
                
                run_async(st.session_state.progress_tracker.track_lesson_completion(result))
                st.rerun()

# Vocabulary Page
elif page == "📖 Vocabulary":
    st.header("📖 Vocabulary Builder")
    
    progress = st.session_state.progress_tracker.load_progress()
    level = st.selectbox("Level:", ["A1", "A2", "B1", "B2", "C1", "C2"],
                         index=["A1", "A2", "B1", "B2", "C1", "C2"].index(progress['current_level']))
    
    word = st.text_input("Enter German word:", placeholder="e.g., Fahrzeug")
    
    if st.button("Analyze", use_container_width=True):
        if word:
            with st.spinner("Analyzing..."):
                result = run_async(
                    st.session_state.orchestrator.orchestrate_learning(
                        text=word,
                        level=level,
                        goal="vocabulary analysis"
                    )
                )
                
                if result['success']:
                    vocab_insights = result['comprehensive_lesson'].get('vocabulary_insights', {})
                    
                    for analyzed_word, analysis in vocab_insights.items():
                        st.success(f"**{analyzed_word}**")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Level", analysis.get('level', 'Unknown'))
                        with col2:
                            st.metric("Compound", "Yes" if analysis.get('is_compound') else "No")
                        with col3:
                            st.metric("Difficulty", analysis.get('difficulty', 'unknown').title())
                        
                        if result['comprehensive_lesson'].get('learning_plan'):
                            st.subheader("📋 Tips")
                            for tip in result['comprehensive_lesson']['learning_plan']:
                                st.write(f"• {tip}")
                    
                    run_async(st.session_state.progress_tracker.track_lesson_completion(result))

# Grammar Page
elif page == "📝 Grammar":
    st.header("📝 Grammar Analysis")
    
    progress = st.session_state.progress_tracker.load_progress()
    level = st.selectbox("Level:", ["A1", "A2", "B1", "B2", "C1", "C2"],
                         index=["A1", "A2", "B1", "B2", "C1", "C2"].index(progress['current_level']))
    
    sentence = st.text_area("Enter German sentence:", 
                            placeholder="e.g., Der große Hund läuft schnell.")
    
    if st.button("Analyze", use_container_width=True):
        if sentence:
            with st.spinner("Analyzing..."):
                result = run_async(
                    st.session_state.orchestrator.orchestrate_learning(
                        text=sentence,
                        level=level,
                        goal="grammar analysis"
                    )
                )
                
                if result['success']:
                    grammar = result['comprehensive_lesson'].get('grammar_insights', {})
                    
                    st.success("✅ Analysis complete!")
                    
                    if grammar.get('main_structures'):
                        st.subheader("🏗️ Main Structures")
                        st.write(grammar['main_structures'])
                    
                    if grammar.get('learning_tip'):
                        st.info(f"💡 **Tip:** {grammar['learning_tip']}")
                    
                    if result['comprehensive_lesson'].get('learning_plan'):
                        st.subheader("📋 Learning Plan")
                        for step in result['comprehensive_lesson']['learning_plan']:
                            st.write(f"✅ {step}")
                    
                    run_async(st.session_state.progress_tracker.track_lesson_completion(result))

# Progress Page
elif page == "📈 Progress":
    st.header("📈 Your Progress")
    
    progress = st.session_state.progress_tracker.load_progress()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Status")
        st.metric("Level", progress['current_level'])
        st.metric("Target", progress['target_level'])
        st.metric("Streak", f"{progress['learning_streak']} days")
        st.metric("Sessions", progress['total_sessions'])
    
    with col2:
        st.subheader("📚 Knowledge")
        st.metric("Words", len(progress['vocabulary_learned']))
        st.metric("Grammar", len(progress['grammar_patterns_mastered']))
    
    st.markdown("---")
    
    st.subheader("📖 Recent Vocabulary")
    if progress['vocabulary_learned']:
        recent = list(progress['vocabulary_learned'].items())[-10:]
        for word, data in reversed(recent):
            with st.expander(f"**{word}** ({data.get('level', 'unknown')})"):
                st.write(f"Learned: {data.get('learned_date', 'Unknown')[:10]}")
                st.write(f"Compound: {'Yes' if data.get('is_compound') else 'No'}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🇩🇪 German Learning Assistant | Powered by LangGraph & Groq AI</p>
    </div>
    """, 
    unsafe_allow_html=True
)