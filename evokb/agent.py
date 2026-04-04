# Re-export from evokb.agents for backward compatibility


def __getattr__(name):
    if name == "AgentClassifier":
        from evokb.agents.agent import AgentClassifier

        return AgentClassifier
    elif name == "classify_query":
        from evokb.agents.agent import classify_query

        return classify_query
    elif name == "classify_query_details":
        from evokb.agents.agent import classify_query_details

        return classify_query_details
    elif name == "QueryIntent":
        from evokb.agents.agent import QueryIntent

        return QueryIntent
    elif name == "completion":
        from litellm import completion

        return completion
    raise AttributeError(f"module 'evokb.agent' has no attribute '{name}'")
