import wikipedia


# ======================================
# MAIN FUNCTION
# ======================================

def generate_ai_content(user_query):

    try:

        # SEARCH TOPIC

        search_results = wikipedia.search(user_query)

        # CHECK RESULTS

        if len(search_results) == 0:

            return f"No content found for '{user_query}'"

        # TAKE FIRST RESULT

        topic = search_results[0]

        # GET PAGE

        page = wikipedia.page(topic)

        # FULL CONTENT

        content = page.content

        # FORMAT OUTPUT

        formatted_content = f"""

{topic.upper()}

====================================================

{content}

"""

        # RETURN LARGE CONTENT

        return formatted_content[:20000]

    except Exception as e:

        return f"Error: {str(e)}"