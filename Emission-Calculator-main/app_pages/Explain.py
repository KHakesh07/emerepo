import streamlit as st

def explain_page():
    st.set_page_config(page_title="Emission Overview", page_icon="🌍")
    st.title("Emission Overview")
    st.write("Understanding the different scopes of emissions is crucial for effective carbon footprint management.")

    st.write(
        "Emissions refer to the release of gases, particles, or pollutants into the atmosphere from various sources. "
        "These emissions can originate from natural processes (such as volcanic eruptions or wildfires) or human activities "
        "(such as burning fossil fuels, industrial processes, and agriculture)."
    )

    st.write("The emissions can be categorized into three scopes:")
    st.write(
        "These three categories are used in Greenhouse Gas (GHG) accounting to measure and report emissions from different sources. "
        "They help organizations track their carbon footprint and take action to reduce it."
    )

    # Scope 1
    with st.expander("🔍 **Scope 1: Direct Emissions**"):
        st.write(
            "Scope 1 emissions are direct emissions from sources owned or controlled by a company. "
            "Examples include emissions from company vehicles, on-site fuel combustion, and industrial processes."
        )
        st.image("https://via.placeholder.com/600x200.png?text=Scope+1+Example", use_container_width=True)

    # Scope 2
    with st.expander("🔍 **Scope 2: Indirect Emissions**"):
        st.write(
            "Scope 2 emissions are indirect emissions from the generation of purchased electricity, heating, or cooling consumed by a company. "
            "These emissions occur at the facility where the energy is generated but are attributed to the company that consumes the energy."
        )
        st.image("https://via.placeholder.com/600x200.png?text=Scope+2+Example", use_container_width=True)

    # Scope 3
    with st.expander("🔍 **Scope 3: Indirect Emissions from the Supply Chain**"):
        st.write(
            "Scope 3 emissions are indirect emissions from sources not owned or controlled by the company but related to its activities. "
            "Examples include emissions from employee commuting, business travel, and the production of purchased goods and services."
        )
        st.image("https://via.placeholder.com/600x200.png?text=Scope+3+Example", use_container_width=True)

    st.subheader("Why These Emissions Matter")
    st.write(
        "Addressing all three scopes is vital for achieving net-zero goals, improving sustainability, meeting regulatory requirements, "
        "and gaining consumer trust in an increasingly environmentally conscious world. 🌍💚"
    )

    st.subheader("How Do We Calculate These Emissions")
    st.markdown("<h4>Emissions = Activity Data x Emission Factor</h4>", unsafe_allow_html=True)

    st.subheader("Why Are Emissions Important?")
    st.write(
        """
        - **Climate Change:** GHGs trap heat in the atmosphere, contributing to global warming.
        - **Air Pollution & Health Risks:** Pollutants can cause respiratory issues, heart diseases, and other health problems.
        - **Environmental Impact:** Emissions lead to phenomena such as acid rain, ocean acidification, and ecosystem disruption.
        - **Mitigation Efforts:** Strategies like renewable energy adoption, energy efficiency, carbon capture, and policy initiatives (e.g., the Paris Agreement) are key to reducing emissions.
        """
    )