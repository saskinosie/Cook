import streamlit as st
import os
import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth
from weaviate_agents.query import QueryAgent

# Load environment variables (if running locally)
if "WEAVIATE_URL" in st.secrets:
    WEAVIATE_URL = st.secrets["WEAVIATE_URL"]
    WEAVIATE_API_KEY = st.secrets["WEAVIATE_API_KEY"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv()
    WEAVIATE_URL = os.getenv("WEAVIATE_URL")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.title("Loren Cook Query Assistant")
st.write("Query the Loren Cook test collection using Weaviate + OpenAI.")

# Input from the user
user_query = st.text_input("Enter your question:", "")

if not WEAVIATE_URL or not WEAVIATE_API_KEY or not OPENAI_API_KEY:
    st.error("Missing API keys or endpoints. Please configure them in Streamlit Secrets or a .env file.")
else:
    headers = {
        "X-OpenAI-Api-Key": OPENAI_API_KEY,
    }

    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=WEAVIATE_URL,
            auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
            headers=headers,
        )

        qa = QueryAgent(client=client, collections=["Cookbook"])

        if st.button("Submit Query"):
            with st.spinner("Getting answer from Weaviate..."):
                response = qa.run(user_query)
                st.subheader("Final Answer")
                st.markdown(response.final_answer if hasattr(response, "final_answer") else "No answer generated.")

                with st.expander("See details"):
                    st.markdown("**Original Query:** " + getattr(response, "original_question", "N/A"))

                    if hasattr(response, "searches") and len(response.searches) > 0:
                        first_search = response.searches[0]
                        if hasattr(first_search, "queries"):
                            st.markdown("**Generated Search:** " + ", ".join(first_search.queries))
                        else:
                            st.markdown("**Generated Search:** N/A")
                    else:
                        st.markdown("**Generated Search:** None")

                    sources = getattr(response, "sources", [])
                    if sources:
                        source_ids = ", ".join([s.object_id for s in sources])
                        st.markdown("**Sources:** " + source_ids)
                    else:
                        st.markdown("**Sources:** None")

        client.close()
    except Exception as e:
        st.error(f"Something went wrong: {e}")
