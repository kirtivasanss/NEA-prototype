import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama


# Initialize Ollama LLM
def get_llm():
    return Ollama(
        base_url="http://localhost:11434",
        model="llama2"
    )


# Define agent creation functions
def create_storyteller(llm):
    return Agent(
        name="Storyteller",
        role="Master Storyteller",
        goal="Guide players through an immersive RPG adventure",
        backstory="An ancient narrator who weaves the fate of all adventurers",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )


def create_warrior(llm):
    return Agent(
        name="Warrior",
        role="Fighter",
        goal="Defend the kingdom and battle foes",
        backstory="A seasoned warrior trained in the art of combat, sworn to protect the realm",
        verbose=True,
        allow_delegation=True,
        llm=llm
    )


def create_mage(llm):
    return Agent(
        name="Mage",
        role="Wizard",
        goal="Use magic to aid allies and defeat dark forces",
        backstory="A wise and powerful sorcerer who seeks knowledge and mastery over arcane arts",
        verbose=True,
        allow_delegation=True,
        llm=llm
    )


def create_rogue(llm):
    return Agent(
        name="Rogue",
        role="Thief",
        goal="Sneak through shadows and uncover secrets",
        backstory="A cunning and agile rogue who relies on stealth and deception to survive",
        verbose=True,
        allow_delegation=True,
        llm=llm
    )


# Create tasks based on user input
def create_task(agents, user_input):
    return Task(
        description="Generate an engaging RPG response that advances the story while staying true to each character.",
        expected_output="""
        A detailed narrative response that includes:
        - Character dialogue and actions
        - Environmental descriptions
        - Story progression
        - Narrative cohesion with previous interactions
        The response should be formatted in clear, readable text with proper paragraphs.
        """,
        context=f"""
        User Input: {user_input}

        Consider the following when generating the response:
        1. The current context and flow of the story
        2. Each character's unique personality and abilities
        3. Maintaining narrative consistency
        4. Creating opportunities for character interaction
        """,
        agent=agents[0]  # Storyteller is the primary agent
    )


# Initialize Streamlit interface
st.set_page_config(page_title="RPG AI Roleplay", layout="wide")
st.title("RPG AI Roleplay Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "crew" not in st.session_state:
    st.session_state.crew = None

# Sidebar for character selection
st.sidebar.title("Select Your Characters")
available_roles = ["Warrior", "Mage", "Rogue"]
selected_roles = st.sidebar.multiselect(
    "Choose your party members:",
    available_roles,
    default=["Warrior"]
)

# Initialize or update crew when selection changes
if st.session_state.crew is None or "last_selection" not in st.session_state or st.session_state.last_selection != selected_roles:
    llm = get_llm()
    storyteller = create_storyteller(llm)

    # Create selected agents
    selected_agents = [storyteller]  # Storyteller is always included
    if "Warrior" in selected_roles:
        selected_agents.append(create_warrior(llm))
    if "Mage" in selected_roles:
        selected_agents.append(create_mage(llm))
    if "Rogue" in selected_roles:
        selected_agents.append(create_rogue(llm))

    st.session_state.crew = Crew(
        agents=selected_agents,
        process=Process.sequential,
        verbose=True
    )
    st.session_state.last_selection = selected_roles

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
user_input = st.chat_input("What would you like to do?")
if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            task = create_task(st.session_state.crew.agents, user_input)
            response = st.session_state.crew.kickoff([task])  # Pass task as a list
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})