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
        color: #000000; /* Black text for contrast */
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Dashboard"

# Helper function to run async code
def run_async(coro):
    """Run async function in streamlit"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None
    finally:
        loop.close()

# Main title
st.markdown('<h1 class="main-header">German Learning Assistant</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Navigation")
    
    page = st.radio(
        "Choose a section:",
        ["📊 Dashboard", "📚 Daily Lesson", "💬 Conversation", 
         "📖 Vocabulary", "📝 Grammar", "📈 Progress"],
        key='page_navigation',
        index=["📊 Dashboard", "📚 Daily Lesson", "💬 Conversation", 
               "📖 Vocabulary", "📝 Grammar", "📈 Progress"].index(st.session_state.current_page)
    )
    
    # Update current page
    st.session_state.current_page = page
    
    st.markdown("---")
    
    # Quick stats
    progress = st.session_state.progress_tracker.load_progress()
    st.metric("🔥 Streak", f"{progress['learning_streak']} days")
    st.metric("📊 Level", progress['current_level'])
    st.metric("📚 Words", len(progress['vocabulary_learned']))

# Use current_page instead of page variable
current_page = st.session_state.current_page

# Dashboard Page
if current_page == "📊 Dashboard":
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
    
    # Quick actions with navigation
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Start Today's Lesson", use_container_width=True, key="btn_lesson"):
            st.session_state.current_page = "📚 Daily Lesson"
            st.rerun()
    
    with col2:
        if st.button("💬 Practice Conversation", use_container_width=True, key="btn_conv"):
            st.session_state.current_page = "💬 Conversation"
            st.rerun()
    
    with col3:
        if st.button("📊 View Progress", use_container_width=True, key="btn_progress"):
            st.session_state.current_page = "📈 Progress"
            st.rerun()
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📅 Recent Activity")
    if progress['lessons_completed']:
        recent_lessons = progress['lessons_completed'][-5:]
        for lesson in reversed(recent_lessons):
            with st.expander(f"📝 Lesson from {lesson['date'][:10]}", expanded=False):
                st.write(f"**Level:** {lesson['level']}")
                if lesson['words_learned']:
                    st.write(f"**Words:** {', '.join(lesson['words_learned'][:5])}")
                if lesson['grammar_points']:
                    st.write(f"**Grammar:** {', '.join(lesson['grammar_points'])}")
    else:
        st.info("🎯 No lessons completed yet. Start your first lesson today!")

# Daily Lesson Page
elif current_page == "📚 Daily Lesson":
    st.header("📚 Your Personalized Daily Lesson")
    
    with st.spinner("🔄 Generating your personalized lesson..."):
        daily_lesson = run_async(st.session_state.progress_tracker.generate_daily_lesson())
    
    if daily_lesson:
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
            st.info("💡 Complete some lessons to build your vocabulary!")
        
        st.markdown("---")
        
        # Main exercises
        st.subheader("🎯 Main Exercises")
        
        for idx, exercise in enumerate(lesson_content['main_exercises'], 1):
            st.markdown(f"### Exercise {idx}: {exercise['type'].replace('_', ' ').title()}")
            st.write(f"**Focus:** {exercise['focus']}")
            
            if exercise['type'] == 'grammar_analysis':
                user_input = st.text_area(
                    "📝 Analyze this sentence:",
                    value=exercise['sentence'],
                    key=f"grammar_{idx}",
                    height=80
                )
                
                if st.button("🔍 Analyze Grammar", key=f"analyze_grammar_{idx}", type="primary"):
                    with st.spinner("🔄 Analyzing grammar..."):
                        result = run_async(
                            st.session_state.orchestrator.orchestrate_learning(
                                text=user_input,
                                level=daily_lesson['user_level'],
                                goal="grammar analysis"
                            )
                        )
                        
                        if result and result['success']:
                            lesson = result['comprehensive_lesson']
                            st.success("✅ Grammar analysis complete!")
                            
                            with st.expander("📚 Grammar Insights", expanded=True):
                                st.write(f"**Main Structures:** {lesson['grammar_insights'].get('main_structures', 'N/A')}")
                                st.write(f"**💡 Tip:** {lesson['grammar_insights'].get('learning_tip', 'N/A')}")
                                
                                if lesson['grammar_insights'].get('common_mistakes'):
                                    st.write("**⚠️ Common Mistakes:**")
                                    for mistake in lesson['grammar_insights']['common_mistakes']:
                                        st.write(f"  • {mistake}")
                            
                            run_async(st.session_state.progress_tracker.track_lesson_completion(result))
            
            elif exercise['type'] == 'vocabulary_building':
                user_word = st.text_input(
                    "📖 Analyze this word:",
                    value=exercise['word'],
                    key=f"vocab_{idx}"
                )
                
                if st.button("🔍 Analyze Word", key=f"analyze_vocab_{idx}", type="primary"):
                    with st.spinner("🔄 Analyzing vocabulary..."):
                        result = run_async(
                            st.session_state.orchestrator.orchestrate_learning(
                                text=user_word,
                                level=daily_lesson['user_level'],
                                goal="vocabulary analysis"
                            )
                        )
                        
                        if result and result['success']:
                            lesson = result['comprehensive_lesson']
                            st.success("✅ Vocabulary analysis complete!")
                            
                            with st.expander("📖 Vocabulary Insights", expanded=True):
                                for word, analysis in lesson['vocabulary_insights'].items():
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Word:** {word}")
                                        st.write(f"**Level:** {analysis['level']}")
                                    with col2:
                                        st.write(f"**Compound:** {'Yes ✓' if analysis['is_compound'] else 'No'}")
                                        st.write(f"**Difficulty:** {analysis['difficulty'].title()}")
                            
                            run_async(st.session_state.progress_tracker.track_lesson_completion(result))
            
            st.markdown("---")

# Conversation Page
elif current_page == "💬 Conversation":
    st.header("💬 Practice German Conversation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        progress = st.session_state.progress_tracker.load_progress()
        level = st.selectbox(
            "📊 Your Level:", 
            ["A1", "A2", "B1", "B2", "C1", "C2"], 
            index=["A1", "A2", "B1", "B2", "C1", "C2"].index(progress['current_level']),
            key="conv_level"
        )
    
    with col2:
        scenario = st.selectbox(
            "🎭 Scenario:", 
            ["casual", "restaurant", "shopping", "travel", "work", "formal"],
            key="conv_scenario"
        )
    
    with col3:
        enable_audio = st.checkbox(
            "🔊 Enable Audio",
            value=True,
            help="Generate German audio for AI responses"
        )
    
    st.markdown("---")
    
    # Conversation display
    st.subheader("💭 Conversation")
    
    if st.session_state.conversation_history:
        for idx, msg in enumerate(st.session_state.conversation_history):
            if msg['role'] == 'user':
                st.markdown(f"**👤 You:** {msg['content']}")
            else:
                # Bot response with audio player
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"**🤖 AI Partner:** {msg['content']}")
                    if msg.get('translation'):
                        st.caption(f"📝 Translation: {msg['translation']}")
                
                with col2:
                    # Audio player if available
                    if msg.get('audio_file'):
                        try:
                            # Check if file exists
                            from pathlib import Path
                            audio_path = Path(msg['audio_file'])
                            if audio_path.exists():
                                st.audio(str(audio_path), format='audio/mp3')
                            else:
                                st.caption("🔇 Audio expired")
                        except Exception as e:
                            st.caption("🔇 Audio unavailable")
                    else:
                        st.caption("🔇 No audio")
        
        st.markdown("---")
    else:
        st.info("💡 Start a conversation in German! The AI will respond with audio and help you learn.")
        
        # Show conversation starters
        with st.expander("💬 Need conversation starters?", expanded=False):
            st.write(f"**Try these {level} level phrases:**")
            # Get starters from conversation agent
            from agents.conversation_practice import ConversationPracticeAgent
            agent = ConversationPracticeAgent()
            starters = agent.suggest_conversation_starters(level)
            for starter in starters:
                if st.button(f"💬 {starter}", key=f"starter_{starter}", use_container_width=True):
                    st.session_state.conversation_input = starter
                    st.rerun()
    
    # User input
    user_message = st.text_input(
        "✍️ Your message in German:", 
        key="conv_input",
        placeholder="z.B. Guten Tag! Wie geht es Ihnen?",
        value=st.session_state.get('conversation_input', '')
    )
    
    # Clear the prefilled input after use
    if 'conversation_input' in st.session_state:
        del st.session_state.conversation_input
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        send_button = st.button("📤 Send", use_container_width=True, type="primary")
    
    with col2:
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()
    
    if send_button and user_message:
        st.session_state.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        with st.spinner("🤔 Thinking and generating audio..."):
            result = run_async(
                st.session_state.orchestrator.orchestrate_learning(
                    text=user_message,
                    level=level,
                    goal="conversation practice",
                    context={
                        "topic": scenario, 
                        "scenario": scenario,
                        "generate_audio": enable_audio  # Pass audio preference
                    }
                )
            )
            
            if result and result['success']:
                conv_data = result['comprehensive_lesson'].get('conversation_practice', {})
                
                msg_data = {
                    'role': 'assistant',
                    'content': conv_data.get('suggested_response', 'Entschuldigung, ich verstehe nicht.'),
                    'translation': conv_data.get('translation', '')
                }
                
                # Add audio file path if available
                if conv_data.get('audio_file'):
                    msg_data['audio_file'] = conv_data['audio_file']
                
                st.session_state.conversation_history.append(msg_data)
                
                run_async(st.session_state.progress_tracker.track_lesson_completion(result))
                st.rerun()

# Vocabulary Page
elif current_page == "📖 Vocabulary":
    st.header("📖 German Vocabulary Builder")
    st.write("Analyze German words, especially compound words, to understand their structure.")
    
    progress = st.session_state.progress_tracker.load_progress()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        word = st.text_input(
            "🔤 Enter a German word:", 
            placeholder="e.g., Fahrzeug, Krankenhaus, Umweltschutz",
            key="vocab_word"
        )
    
    with col2:
        level = st.selectbox(
            "📊 Your Level:", 
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            index=["A1", "A2", "B1", "B2", "C1", "C2"].index(progress['current_level']),
            key="vocab_level"
        )
    
    if st.button("🔍 Analyze Word", use_container_width=True, type="primary"):
        if word:
            with st.spinner("🔄 Analyzing vocabulary..."):
                result = run_async(
                    st.session_state.orchestrator.orchestrate_learning(
                        text=word,
                        level=level,
                        goal="vocabulary analysis"
                    )
                )
                
                if result and result['success']:
                    vocab_insights = result['comprehensive_lesson'].get('vocabulary_insights', {})
                    
                    for analyzed_word, analysis in vocab_insights.items():
                        st.success(f"✅ Analysis for: **{analyzed_word}**")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Estimated Level", analysis.get('level', 'Unknown'))
                        with col2:
                            is_compound = analysis.get('is_compound', False)
                            st.metric("🔧 Compound Word", "Yes ✓" if is_compound else "No")
                        with col3:
                            difficulty = analysis.get('difficulty', 'unknown')
                            st.metric("📈 Difficulty", difficulty.title())
                        
                        if result['comprehensive_lesson'].get('learning_plan'):
                            st.markdown("### 📋 Learning Tips")
                            for tip in result['comprehensive_lesson']['learning_plan']:
                                st.write(f"💡 {tip}")
                    
                    run_async(st.session_state.progress_tracker.track_lesson_completion(result))
        else:
            st.warning("⚠️ Please enter a German word to analyze.")

# Grammar Page
elif current_page == "📝 Grammar":
    st.header("📝 German Grammar Analysis")
    st.write("Analyze German sentences to understand grammar structures, cases, and verb conjugations.")
    
    progress = st.session_state.progress_tracker.load_progress()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        sentence = st.text_area(
            "✍️ Enter a German sentence:", 
            placeholder="e.g., Der große Hund läuft schnell im Park.",
            height=100,
            key="grammar_sentence"
        )
    
    with col2:
        level = st.selectbox(
            "📊 Your Level:", 
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            index=["A1", "A2", "B1", "B2", "C1", "C2"].index(progress['current_level']),
            key="grammar_level"
        )
    
    if st.button("🔍 Analyze Grammar", use_container_width=True, type="primary"):
        if sentence:
            with st.spinner("🔄 Analyzing grammar..."):
                result = run_async(
                    st.session_state.orchestrator.orchestrate_learning(
                        text=sentence,
                        level=level,
                        goal="grammar analysis"
                    )
                )
                
                if result and result['success']:
                    grammar = result['comprehensive_lesson'].get('grammar_insights', {})
                    
                    st.success("✅ Grammar analysis complete!")
                    
                    if grammar.get('main_structures'):
                        st.markdown("### 🏗️ Main Grammatical Structures")
                        st.write(grammar['main_structures'])
                    
                    if grammar.get('learning_tip'):
                        st.info(f"💡 **Learning Tip:** {grammar['learning_tip']}")
                    
                    if grammar.get('common_mistakes'):
                        st.markdown("### ⚠️ Common Mistakes to Avoid")
                        for mistake in grammar['common_mistakes']:
                            st.write(f"• {mistake}")
                    
                    if result['comprehensive_lesson'].get('learning_plan'):
                        st.markdown("### 📋 Learning Plan")
                        for idx, step in enumerate(result['comprehensive_lesson']['learning_plan'], 1):
                            st.write(f"{idx}. {step}")
                    
                    run_async(st.session_state.progress_tracker.track_lesson_completion(result))
        else:
            st.warning("⚠️ Please enter a German sentence to analyze.")

# Progress Page
elif current_page == "📈 Progress":
    st.header("📈 Your Learning Progress")
    
    progress = st.session_state.progress_tracker.load_progress()
    
    # Progress overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Current Status")
        st.metric("Current Level", progress['current_level'], delta=None)
        st.metric("Target Level", progress['target_level'])
        st.metric("Learning Streak", f"{progress['learning_streak']} days", delta="+1" if progress['learning_streak'] > 0 else None)
        st.metric("Total Sessions", progress['total_sessions'])
    
    with col2:
        st.subheader("📚 Knowledge Base")
        st.metric("Words Learned", len(progress['vocabulary_learned']))
        st.metric("Grammar Patterns Mastered", len(progress['grammar_patterns_mastered']))
        
        completion_rate = (progress['learning_streak'] / 7) if progress['learning_streak'] <= 7 else 1.0
        st.metric("Weekly Completion", f"{int(completion_rate * 100)}%")
    
    st.markdown("---")
    
    # Recent vocabulary
    st.subheader("📖 Recently Learned Vocabulary")
    if progress['vocabulary_learned']:
        recent_vocab = list(progress['vocabulary_learned'].items())[-10:]
        
        for word, data in reversed(recent_vocab):
            with st.expander(f"**{word}** ({data.get('level', 'unknown')} level)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Learned:** {data.get('learned_date', 'Unknown')[:10]}")
                    st.write(f"**Mastery:** {data.get('mastery_level', 'introduced').title()}")
                with col2:
                    st.write(f"**Compound:** {'Yes ✓' if data.get('is_compound') else 'No'}")
                    st.write(f"**Level:** {data.get('level', 'unknown')}")
    else:
        st.info("💡 Start learning to build your vocabulary library!")
    
    st.markdown("---")
    
    # Grammar patterns
    st.subheader("📝 Grammar Patterns Mastered")
    if progress['grammar_patterns_mastered']:
        for idx, pattern in enumerate(progress['grammar_patterns_mastered'], 1):
            st.write(f"{idx}. ✅ {pattern}")
    else:
        st.info("💡 Complete grammar exercises to track your progress!")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>German Learning Assistant | Powered by LangGraph & Groq AI</p>
        <p>Keep learning every day! 🚀</p>
    </div>
    """, 
    unsafe_allow_html=True
)